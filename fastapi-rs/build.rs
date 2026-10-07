//! Verify the metadata-pinned Starlette-RS source before compiling FastAPI-RS.

use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{self, Command};

const STARLETTE_SOURCE_PATHS: [&str; 7] = [
    "Cargo.toml",
    "starlette-rs/Cargo.toml",
    "starlette-rs/src",
    "starlette-rs-py/Cargo.toml",
    "starlette-rs-py/src",
    "starlette-rs-py/python",
    "starlette-rs-py/pyproject.toml",
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
    println!("cargo:rerun-if-changed={}", workspace_manifest.display());
    println!("cargo:rerun-if-changed={}", metadata_path.display());

    let workspace_manifest_text = fs::read_to_string(&workspace_manifest)
        .map_err(|error| format!("cannot read {}: {error}", workspace_manifest.display()))?;
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

    let expected_revision = pinned_starlette_rs_revision(
        &fs::read_to_string(&metadata_path)
            .map_err(|error| format!("cannot read {}: {error}", metadata_path.display()))?,
    )?;
    if expected_revision.len() != 40
        || !expected_revision
            .bytes()
            .all(|character| character.is_ascii_hexdigit())
    {
        return Err(format!(
            "metadata.yaml has an invalid Starlette-RS commit pin: {expected_revision}"
        ));
    }

    let repository_root = git_output(&canonical_source_root, &["rev-parse", "--show-toplevel"])?;
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

    for source_path in STARLETTE_SOURCE_PATHS {
        println!(
            "cargo:rerun-if-changed={}",
            canonical_source_root.join(source_path).display()
        );
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

    println!(
        "cargo:warning=FastAPI-RS verified Starlette-RS source {} at {expected_revision}",
        canonical_source_root.display()
    );
    Ok(())
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

fn pinned_starlette_rs_revision(metadata: &str) -> Result<String, String> {
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
            if let Some(value) = line.strip_prefix("  commit:") {
                return Ok(value.trim().trim_matches('"').to_owned());
            }
        }
    }
    Err("metadata.yaml has no starlette_rs.commit pin".to_owned())
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
