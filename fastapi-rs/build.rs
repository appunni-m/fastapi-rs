//! Verify the metadata-pinned Starlette-RS source before compiling FastAPI-RS.

use sha2::{Digest, Sha256};
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{self, Command};

const STARLETTE_SOURCE_PATHS: [&str; 10] = [
    "Cargo.toml",
    "Cargo.lock",
    "rust-toolchain.toml",
    "starlette-rs/Cargo.toml",
    "starlette-rs/build.rs",
    "starlette-rs/src",
    "starlette-rs-py/Cargo.toml",
    "starlette-rs-py/build.rs",
    "starlette-rs-py/src",
    "starlette-rs-py/python",
];

fn main() {
    if let Err(error) = validate_starlette_rs_source() {
        eprintln!("FastAPI-RS Starlette-RS build identity check failed: {error}");
        process::exit(1);
    }
}

fn validate_starlette_rs_source() -> Result<(), String> {
    let manifest_dir = PathBuf::from(
        env::var_os("CARGO_MANIFEST_DIR")
            .ok_or_else(|| "Cargo did not provide CARGO_MANIFEST_DIR".to_owned())?,
    );
    let workspace_root = manifest_dir
        .parent()
        .ok_or_else(|| "FastAPI-RS package has no workspace parent".to_owned())?;
    let workspace_manifest = workspace_root.join("Cargo.toml");
    let metadata_path = workspace_root.join("metadata.yaml");
    if !workspace_manifest.exists() && !metadata_path.exists() {
        return validate_packaged_contract(&manifest_dir);
    }
    if !workspace_manifest.is_file() || !metadata_path.is_file() {
        return Err(format!(
            "workspace identity inputs are incomplete beside {}",
            manifest_dir.display()
        ));
    }
    println!("cargo:rerun-if-changed={}", workspace_manifest.display());
    println!("cargo:rerun-if-changed={}", metadata_path.display());

    let workspace_manifest_text = fs::read_to_string(&workspace_manifest)
        .map_err(|error| format!("cannot read {}: {error}", workspace_manifest.display()))?;
    let metadata_text = fs::read_to_string(&metadata_path)
        .map_err(|error| format!("cannot read {}: {error}", metadata_path.display()))?;
    let expected_version = pinned_starlette_rs_value(&metadata_text, "distribution_version")?;
    let dependency_version = workspace_dependency_version(&workspace_manifest_text)?;
    if dependency_version != format!("={expected_version}") {
        return Err(format!(
            "workspace starlette-rs dependency must require ={} to match metadata.yaml, found {dependency_version}",
            expected_version
        ));
    }
    let dependency_path = workspace_dependency_path(&workspace_manifest_text)?;
    let package_root = workspace_root
        .join(dependency_path)
        .canonicalize()
        .map_err(|error| format!("cannot resolve Starlette-RS Cargo package: {error}"))?;
    if package_root.file_name().and_then(|name| name.to_str()) != Some("starlette-rs") {
        return Err(format!(
            "workspace dependency resolves to {}, expected the starlette-rs package directory",
            package_root.display()
        ));
    }
    let dependency_manifest = package_root.join("Cargo.toml");
    if !dependency_manifest.is_file() {
        return Err(format!(
            "Starlette-RS Cargo manifest is missing: {}",
            dependency_manifest.display()
        ));
    }
    let source_root = package_root
        .parent()
        .ok_or_else(|| "Starlette-RS package has no source repository root".to_owned())?;
    let canonical_source_root = source_root
        .canonicalize()
        .map_err(|error| format!("cannot resolve Starlette-RS repository root: {error}"))?;
    for source_path in STARLETTE_SOURCE_PATHS {
        println!(
            "cargo:rerun-if-changed={}",
            canonical_source_root.join(source_path).display()
        );
    }

    let expected_revision = pinned_starlette_rs_value(&metadata_text, "commit")?;
    let expected_source_digest = pinned_starlette_rs_value(&metadata_text, "source_tree_sha256")?;
    validate_starlette_rs_pin(
        &expected_version,
        &expected_revision,
        &expected_source_digest,
    )?;

    let repository_root = match git_output(
        &canonical_source_root,
        &["rev-parse", "--show-toplevel"],
    ) {
        Ok(repository_root) => repository_root,
        Err(git_error) => {
            let vendored_root = workspace_root
                .join("starlette-rs")
                .canonicalize()
                .map_err(|error| format!("cannot resolve vendored Starlette-RS source: {error}"))?;
            if canonical_source_root != vendored_root {
                return Err(git_error);
            }
            verify_source_tree_digest(&canonical_source_root, &expected_source_digest, false)?;
            println!(
                "cargo:warning=FastAPI-RS verified vendored Starlette-RS source {expected_revision} by SHA-256"
            );
            return Ok(());
        }
    };
    let canonical_repository_root = PathBuf::from(repository_root)
        .canonicalize()
        .map_err(|error| format!("cannot resolve Starlette-RS Git root: {error}"))?;
    if canonical_repository_root != canonical_source_root {
        return Err(format!(
            "Cargo path {} is not the root of its Git checkout {}",
            canonical_source_root.display(),
            canonical_repository_root.display()
        ));
    }

    watch_git_identity_files(&canonical_source_root)?;

    let actual_revision = git_output(&canonical_source_root, &["rev-parse", "HEAD"])?;
    if actual_revision != expected_revision {
        return Err(format!(
            "metadata.yaml pins {expected_revision}, but Cargo resolved {} at {actual_revision}; select the pinned clean Starlette-RS checkout",
            canonical_source_root.display()
        ));
    }

    let mut status_arguments = vec!["status", "--porcelain", "--untracked-files=all", "--"];
    status_arguments.extend(STARLETTE_SOURCE_PATHS);
    let source_changes = git_output(&canonical_source_root, &status_arguments)?;
    if !source_changes.is_empty() {
        return Err(format!(
            "Starlette-RS implementation sources at {expected_revision} are dirty; normal FastAPI-RS builds require a clean pinned checkout:\n{source_changes}"
        ));
    }
    verify_source_tree_digest(&canonical_source_root, &expected_source_digest, true)?;

    println!(
        "cargo:warning=FastAPI-RS verified Starlette-RS source {} at {expected_revision}",
        canonical_source_root.display()
    );
    Ok(())
}

fn validate_packaged_contract(manifest_dir: &Path) -> Result<(), String> {
    let manifest_path = manifest_dir.join("Cargo.toml");
    println!("cargo:rerun-if-changed={}", manifest_path.display());
    let manifest = fs::read_to_string(&manifest_path)
        .map_err(|error| format!("cannot read {}: {error}", manifest_path.display()))?;
    let package_name = manifest_string(&manifest, "package", "name")?;
    if package_name != "fastapi-rs" {
        return Err(format!(
            "package-local identity contract is only valid for fastapi-rs, found {package_name}"
        ));
    }

    let identity_section = "package.metadata.fastapi-rs.starlette-rs";
    let version = manifest_string(&manifest, identity_section, "version")?;
    let revision = manifest_string(&manifest, identity_section, "commit")?;
    let source_digest = manifest_string(&manifest, identity_section, "source_tree_sha256")?;
    validate_starlette_rs_pin(&version, &revision, &source_digest)?;

    let dependency_version = dependency_version(&manifest, "dependencies")?;
    if dependency_version != format!("={version}") {
        return Err(format!(
            "packaged starlette-rs dependency must require ={version} to match its embedded source identity, found {dependency_version}"
        ));
    }

    println!(
        "cargo:warning=FastAPI-RS packaged crate contract pins Starlette-RS {version} source {revision} (SHA-256 {source_digest})"
    );
    Ok(())
}

fn validate_starlette_rs_pin(
    version: &str,
    revision: &str,
    source_digest: &str,
) -> Result<(), String> {
    if version.trim().is_empty() || version.contains(char::is_whitespace) {
        return Err(format!(
            "invalid Starlette-RS distribution version: {version}"
        ));
    }
    if revision.len() != 40
        || !revision
            .bytes()
            .all(|character| character.is_ascii_hexdigit())
    {
        return Err(format!("invalid Starlette-RS commit pin: {revision}"));
    }
    if source_digest.len() != 64
        || !source_digest
            .bytes()
            .all(|character| character.is_ascii_hexdigit() && !character.is_ascii_uppercase())
    {
        return Err(format!(
            "invalid Starlette-RS source-tree SHA-256: {source_digest}"
        ));
    }
    Ok(())
}

fn manifest_string(manifest: &str, section: &str, key: &str) -> Result<String, String> {
    let value = section_value(manifest, section, key)?;
    quoted_toml_string(value).map_err(|error| format!("{section}.{key}: {error}"))
}

fn section_value<'a>(manifest: &'a str, section: &str, key: &str) -> Result<&'a str, String> {
    let header = format!("[{section}]");
    let mut in_section = false;
    for line in manifest.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with('[') {
            in_section = trimmed == header;
            continue;
        }
        if !in_section {
            continue;
        }
        if let Some((candidate, value)) = trimmed.split_once('=') {
            if candidate.trim() == key {
                return Ok(value.trim());
            }
        }
    }
    Err(format!("Cargo.toml has no {key} in [{section}]"))
}

fn quoted_toml_string(value: &str) -> Result<String, String> {
    let value = value.trim();
    let Some(value) = value.strip_prefix('"') else {
        return Err(format!("expected a quoted string, found {value}"));
    };
    let Some((string, remainder)) = value.split_once('"') else {
        return Err("unterminated TOML string".to_owned());
    };
    if !remainder.trim().is_empty() {
        return Err(format!("unexpected content after TOML string: {remainder}"));
    }
    Ok(string.to_owned())
}

fn dependency_version(manifest: &str, section: &str) -> Result<String, String> {
    let dependency = match section_value(manifest, section, "starlette-rs") {
        Ok(dependency) => dependency,
        Err(_) => {
            let dependency_section = format!("{section}.starlette-rs");
            let version = section_value(manifest, &dependency_section, "version")?;
            return quoted_toml_string(version);
        }
    };
    let dependency = dependency.trim();
    if dependency.starts_with('{') {
        let table = dependency
            .strip_prefix('{')
            .and_then(|value| value.strip_suffix('}'))
            .ok_or_else(|| "malformed inline starlette-rs dependency table".to_owned())?;
        for field in table.split(',') {
            if let Some((key, value)) = field.split_once('=') {
                if key.trim() == "version" {
                    return quoted_toml_string(value.trim());
                }
            }
        }
        return Err("starlette-rs dependency table has no version".to_owned());
    }
    quoted_toml_string(dependency)
}

fn workspace_dependency_version(manifest: &str) -> Result<String, String> {
    dependency_version(manifest, "workspace.dependencies")
}

fn workspace_dependency_path(manifest: &str) -> Result<PathBuf, String> {
    let mut in_workspace_dependencies = false;
    for line in manifest.lines() {
        let trimmed = line.trim();
        if trimmed == "[workspace.dependencies]" {
            in_workspace_dependencies = true;
            continue;
        }
        if in_workspace_dependencies && trimmed.starts_with('[') {
            break;
        }
        if in_workspace_dependencies && trimmed.starts_with("starlette-rs =") {
            let path = trimmed
                .split_once("path = \"")
                .map(|(_, rest)| rest)
                .and_then(|rest| rest.split_once('"').map(|(path, _)| path))
                .ok_or_else(|| {
                    "workspace starlette-rs dependency must declare a quoted path".to_owned()
                })?;
            return Ok(PathBuf::from(path));
        }
    }
    Err("Cargo.toml has no starlette-rs path under [workspace.dependencies]".to_owned())
}

fn pinned_starlette_rs_value(metadata: &str, field: &str) -> Result<String, String> {
    let mut in_starlette_rs = false;
    for line in metadata.lines() {
        if line == "starlette_rs:" {
            in_starlette_rs = true;
            continue;
        }
        if in_starlette_rs && !line.starts_with(char::is_whitespace) && !line.trim().is_empty() {
            break;
        }
        if in_starlette_rs {
            if let Some(value) = line.strip_prefix(&format!("  {field}:")) {
                return Ok(value.trim().trim_matches('"').to_owned());
            }
        }
    }
    Err(format!("metadata.yaml has no starlette_rs.{field} pin"))
}

fn verify_source_tree_digest(
    source_root: &Path,
    expected_digest: &str,
    tracked_only: bool,
) -> Result<(), String> {
    let files = if tracked_only {
        git_tracked_source_files(source_root)?
    } else {
        vendored_source_files(source_root)?
    };
    let mut hasher = Sha256::new();
    for relative_path in files {
        let path_text = relative_path
            .to_str()
            .ok_or_else(|| {
                format!(
                    "non-UTF-8 Starlette-RS source path: {}",
                    relative_path.display()
                )
            })?
            .replace('\\', "/");
        hasher.update(path_text.as_bytes());
        hasher.update([0]);
        let contents = fs::read(source_root.join(&relative_path)).map_err(|error| {
            format!(
                "cannot read Starlette-RS source file {}: {error}",
                source_root.join(&relative_path).display()
            )
        })?;
        hasher.update(contents);
        hasher.update([0]);
    }
    let actual_digest = hexadecimal_sha256(&hasher.finalize());
    if actual_digest != expected_digest {
        return Err(format!(
            "metadata.yaml pins Starlette-RS source-tree SHA-256 {expected_digest}, but {} hashes to {actual_digest}",
            source_root.display()
        ));
    }
    Ok(())
}

fn hexadecimal_sha256(digest: &[u8]) -> String {
    const HEX_DIGITS: &[u8; 16] = b"0123456789abcdef";
    let mut encoded = String::with_capacity(digest.len() * 2);
    for byte in digest {
        encoded.push(char::from(HEX_DIGITS[usize::from(byte >> 4)]));
        encoded.push(char::from(HEX_DIGITS[usize::from(byte & 0x0f)]));
    }
    encoded
}

fn git_tracked_source_files(source_root: &Path) -> Result<Vec<PathBuf>, String> {
    let mut arguments = vec!["ls-files", "-z", "--"];
    arguments.extend(STARLETTE_SOURCE_PATHS);
    let output = Command::new("git")
        .arg("-C")
        .arg(source_root)
        .args(arguments)
        .output()
        .map_err(|error| format!("cannot list Starlette-RS source files: {error}"))?;
    if !output.status.success() {
        return Err(format!(
            "git ls-files failed in {}: {}",
            source_root.display(),
            String::from_utf8_lossy(&output.stderr).trim()
        ));
    }
    let mut files = Vec::new();
    for raw_path in output
        .stdout
        .split(|byte| *byte == 0)
        .filter(|path| !path.is_empty())
    {
        let path = std::str::from_utf8(raw_path)
            .map_err(|error| format!("git returned non-UTF-8 Starlette-RS path: {error}"))?;
        let relative_path = PathBuf::from(path);
        if relative_path.is_absolute() || relative_path.starts_with("..") {
            return Err(format!("invalid tracked Starlette-RS source path: {path}"));
        }
        if fs::symlink_metadata(source_root.join(&relative_path))
            .map_err(|error| format!("cannot inspect Starlette-RS source {path}: {error}"))?
            .file_type()
            .is_symlink()
        {
            return Err(format!(
                "Starlette-RS source identity path is a symlink: {path}"
            ));
        }
        files.push(relative_path);
    }
    files.sort_by_key(|path| path.to_string_lossy().replace('\\', "/"));
    if files.is_empty() {
        return Err("no tracked Starlette-RS source files were found".to_owned());
    }
    Ok(files)
}

fn vendored_source_files(source_root: &Path) -> Result<Vec<PathBuf>, String> {
    let mut files = Vec::new();
    for source_path in STARLETTE_SOURCE_PATHS {
        collect_vendored_files(source_root, &source_root.join(source_path), &mut files)?;
    }
    files.sort_by_key(|path| path.to_string_lossy().replace('\\', "/"));
    files.dedup();
    if files.is_empty() {
        return Err("no vendored Starlette-RS source files were found".to_owned());
    }
    Ok(files)
}

fn collect_vendored_files(
    source_root: &Path,
    current_path: &Path,
    files: &mut Vec<PathBuf>,
) -> Result<(), String> {
    let metadata = fs::symlink_metadata(current_path)
        .map_err(|error| format!("cannot inspect vendored Starlette-RS source: {error}"))?;
    if metadata.file_type().is_symlink() {
        return Err(format!(
            "vendored Starlette-RS source contains a symlink: {}",
            current_path.display()
        ));
    }
    if metadata.is_file() {
        files.push(
            current_path
                .strip_prefix(source_root)
                .map_err(|error| format!("vendored Starlette-RS source escaped its root: {error}"))?
                .to_path_buf(),
        );
        return Ok(());
    }
    if !metadata.is_dir() {
        return Err(format!(
            "vendored Starlette-RS source is not a file or directory: {}",
            current_path.display()
        ));
    }
    let mut entries = fs::read_dir(current_path)
        .map_err(|error| format!("cannot read vendored Starlette-RS source: {error}"))?
        .collect::<Result<Vec<_>, _>>()
        .map_err(|error| format!("cannot read vendored Starlette-RS directory entry: {error}"))?;
    entries.sort_by_key(|entry| entry.file_name());
    for entry in entries {
        let path = entry.path();
        let name = entry.file_name();
        let name = name.to_string_lossy();
        if name == "__pycache__"
            || name == "target"
            || name.ends_with(".profraw")
            || name.ends_with(".pyc")
        {
            continue;
        }
        collect_vendored_files(source_root, &path, files)?;
    }
    Ok(())
}

fn git_output(root: &Path, arguments: &[&str]) -> Result<String, String> {
    let output = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(arguments)
        .output()
        .map_err(|error| format!("cannot run git in {}: {error}", root.display()))?;
    if !output.status.success() {
        return Err(format!(
            "git {} failed in {}: {}",
            arguments.join(" "),
            root.display(),
            String::from_utf8_lossy(&output.stderr).trim()
        ));
    }
    String::from_utf8(output.stdout)
        .map(|value| value.trim().to_owned())
        .map_err(|error| format!("git returned non-UTF-8 output: {error}"))
}

fn watch_git_identity_files(root: &Path) -> Result<(), String> {
    for name in ["HEAD", "index", "packed-refs"] {
        let path = git_output(
            root,
            &["rev-parse", "--path-format=absolute", "--git-path", name],
        )?;
        let path = PathBuf::from(path);
        if path.exists() {
            println!("cargo:rerun-if-changed={}", path.display());
        }
    }

    let symbolic_head = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["symbolic-ref", "--quiet", "HEAD"])
        .output()
        .map_err(|error| format!("cannot inspect Starlette-RS HEAD reference: {error}"))?;
    if symbolic_head.status.success() {
        let reference = String::from_utf8(symbolic_head.stdout)
            .map_err(|error| format!("git returned non-UTF-8 HEAD reference: {error}"))?;
        let reference = reference.trim();
        let path = git_output(
            root,
            &[
                "rev-parse",
                "--path-format=absolute",
                "--git-path",
                reference,
            ],
        )?;
        let path = PathBuf::from(path);
        if path.exists() {
            println!("cargo:rerun-if-changed={}", path.display());
        }
    }
    Ok(())
}
