# Draft: OpenAPI metadata and security model source review

**Status:** source and manifest review only. No active candidate, metadata, fixture, recipe, or implementation changes are proposed here. “Supported” below is the atlas source classification; it is not a FastAPI-RS support or parity claim.

## Identity and evidence boundary

- FastAPI source: 0.141.1, commit 95f8322ee1dcda7ceace7b1c4f6c9915b36d748f, in the pinned sibling checkout.
- Python floor: >=3.10; the checked runtime inventory was collected with CPython 3.12.13. Pydantic is 2.13.4. Starlette is 1.6.0.
- Starlette-RS target contract checkout: clean detached /private/tmp/fastapi-rs-starlette-rs-37c6615 at 37c6615e5b54d820d70b9d910d2e06fda8ae4cfe. The selected contract retains the WebSocket scope-mapping operation introduced at dd2c1ac66982218f749f0510758f64f5e61c735b. At the time of this review, 37c changed only sibling benchmark and compatibility-inventory documentation. Later commit 7217 adds input-only generic SchemaGenerator parity coverage and adapter/contract support, with no runtime/dependency/API catalog/review/manifest change. It changes no FastAPI OpenAPI model declaration, candidate, or model-specific contract and therefore does not change this review.
- The source declarations below come from fastapi/openapi/models.py at the FastAPI commit above. Upstream generation/use is traced through FastAPI source. Pydantic-specific constructor signatures, field metadata, validation, extra handling, and encoding behavior are separate runtime behavior; annotations alone do not establish them.
- tests/fixtures/runtime-api-surface-standard.json is the checked Pydantic/Python runtime inventory used below for reflected source signatures and model-field metadata. That inventory is source evidence, not a target comparison.

## Exact atlas inventory count

The named family resolves to **54 API candidate IDs** in tests/fixtures/compatibility-atlas.json:

| Group | Candidate count |
|---|---:|
| Contact and its fields | 4 |
| Info and its fields | 8 |
| License and its fields | 4 |
| SecurityBase and its fields | 3 |
| SecurityScheme union alias | 1 |
| SecuritySchemeType and its enum members | 5 |
| HTTPBase and its fields | 3 |
| HTTPBearer and its fields | 3 |
| OAuth2 and its fields | 3 |
| OAuthFlow and its fields | 3 |
| OAuthFlowAuthorizationCode and its fields | 3 |
| OAuthFlowClientCredentials and its fields | 2 |
| OAuthFlowImplicit and its fields | 2 |
| OAuthFlowPassword and its fields | 2 |
| OAuthFlows and its fields | 5 |
| OpenIdConnect and its fields | 3 |
| **Total** | **54** |

The atlas classifies all 54 as public and supported in its source-candidate inventory. Of these, 49 have operation scope status scope-review-pending; five have scope status slice-described. That split is a manifest review-state split, not a support split. The pinned source names the flow classes OAuthFlowPassword, OAuthFlowAuthorizationCode, OAuthFlowClientCredentials, and OAuthFlowImplicit. It has no OAuthFlowWithPassword, OAuthFlowWithAuthorizationCode, OAuthFlowWithClientCredentials, OAuthFlowWithImplicit, or OAuthFlowWithOpenIdConnect class. OpenIdConnect is a separate class. SecurityScheme is a union type alias, not a Pydantic model class.

## Signature and Pydantic boundary

FastAPI defines BaseModelWithConfig at models.py:57-58 with Pydantic model_config extra=allow. The model classes in this review inherit it, except SecuritySchemeType (an Enum). The class declarations have no explicit __init__. Their reflected Pydantic model constructors have keyword-only field parameters, include **extra_data: Any because of the inherited extra configuration, and return None. The exact reflected parameter facts are summarized here; source field declarations follow in the candidate inventory.

- Contact: name: str | None = None; url: AnyUrl | None = None; email: EmailStr | None = None; **extra_data: Any.
- Info: title: str (required); summary: str | None = None; description: str | None = None; termsOfService: str | None = None; contact: Contact | None = None; license: License | None = None; version: str (required); **extra_data: Any.
- License: name: str (required); identifier: str | None = None; url: AnyUrl | None = None; **extra_data: Any.
- SecurityBase: type: SecuritySchemeType (required; Python field is type_); description: str | None = None; **extra_data: Any.
- HTTPBase: type: SecuritySchemeType = SecuritySchemeType.http; description: str | None = None; scheme: str (required); **extra_data: Any.
- HTTPBearer: type: SecuritySchemeType = SecuritySchemeType.http (inherited); description: str | None = None (inherited); scheme: Literal["bearer"] = "bearer"; bearerFormat: str | None = None; **extra_data: Any.
- OAuth2: type: SecuritySchemeType = SecuritySchemeType.oauth2; description: str | None = None (inherited); flows: OAuthFlows (required); **extra_data: Any.
- OAuthFlow: refreshUrl: str | None = None; scopes: dict[str, str] = {}; **extra_data: Any.
- OAuthFlowAuthorizationCode: inherited refreshUrl and scopes; authorizationUrl: str (required); tokenUrl: str (required); **extra_data: Any.
- OAuthFlowClientCredentials: inherited refreshUrl and scopes; tokenUrl: str (required); **extra_data: Any.
- OAuthFlowImplicit: inherited refreshUrl and scopes; authorizationUrl: str (required); **extra_data: Any.
- OAuthFlowPassword: inherited refreshUrl and scopes; tokenUrl: str (required); **extra_data: Any.
- OAuthFlows: implicit: OAuthFlowImplicit | None = None; password: OAuthFlowPassword | None = None; clientCredentials: OAuthFlowClientCredentials | None = None; authorizationCode: OAuthFlowAuthorizationCode | None = None; **extra_data: Any.
- OpenIdConnect: type: SecuritySchemeType = SecuritySchemeType.openIdConnect; description: str | None = None (inherited); openIdConnectUrl: str (required); **extra_data: Any.
- SecuritySchemeType: Enum runtime signature has one variadic positional parameter, values. SecurityScheme is a types.UnionType value and has no callable constructor signature.

These signatures are reflected source facts in runtime-api-surface-standard.json. The active input recipe direct-api-reference-wave.yaml also has a python.signature probe for Info; its manifest mapping does not include an identity workflow or target comparison. Pydantic 2.13.4 owns runtime interpretation of field annotations, aliases, URL/email types, default handling, validation errors, field order, extra keys, and generated signatures.

No explicit Field constraints or deprecation metadata are declared for this group. The meaningful annotation constraints are the Enum values and HTTPBearer.scheme’s Literal["bearer"] annotation. Contact.url and License.url use Pydantic AnyUrl; Contact.email uses Pydantic EmailStr. The pinned source imports EmailStr when email-validator is available and defines a fallback string validator otherwise (models.py:16-55); this dependency branch is upstream behavior, not a target claim. No candidate in the group has an alias_refs or deprecation_refs entry in the active target manifest. The explicit field alias in the source is type_ → type for SecurityBase and its derived security models.

## Candidate declarations, signatures, and current selector scope

The manifest shorthand used in this inventory is:

- M0: atlas source classification is public/supported; manifest operation scope is scope-review-pending; behavior_contract_state is documentation-fixture-design-linked; operation-level review pending; target_binding.status is full-contract-not-established with rust_binding null; there are no candidate-specific input or identity workflow references.
- MI: M0 plus the one Info class signature input workflow noted below; this still has no identity workflow or target contract.
- M1: manifest operation scope is slice-described with reviewed operation/documentation links, but target_binding.status remains full-contract-not-established. The Rust binding names the partial security model implementation; this is not a complete model contract.
- META and SEC/HTTP/OAUTH/OPENID refer to the input-only recipe observations listed in the next section. A selected generated-document pointer does not prove direct model construction, identity, validation, signature, or serialization parity.

### Info, Contact, and License

- fastapi.openapi.models.Contact — class models.py:61; reflected keyword-only signature as listed above; M0 / META. No direct Contact constructor or identity input.
- fastapi.openapi.models.Contact.name — models.py:62; str | None = None; optional, default None; no alias, explicit constraint, or deprecation; M0 / META selects the containing /info/contact object only, not this leaf.
- fastapi.openapi.models.Contact.url — models.py:63; AnyUrl | None = None; optional, default None; no alias, explicit Field constraint, or deprecation; M0 / META selects the containing object only, not this leaf.
- fastapi.openapi.models.Contact.email — models.py:64; EmailStr | None = None; optional, default None; no alias, explicit Field constraint, or deprecation; M0 / META selects the containing object only, not this leaf.
- fastapi.openapi.models.Info — class models.py:73; reflected keyword-only signature as listed above; MI. Its only candidate-specific active input is direct-api-reference-wave.yaml, case fastapi.direct-api-reference-wave.openapi-info-signature, selector python.signature. It is a signature probe, not identity or output parity.
- fastapi.openapi.models.Info.title — models.py:74; str, required, no default; no alias or deprecation; M0 / META has an exact /info/title selector in docs-reference-openapi.yaml.
- fastapi.openapi.models.Info.summary — models.py:75; str | None = None; optional, default None; no alias or deprecation; M0 / META has exact /info/summary selectors.
- fastapi.openapi.models.Info.description — models.py:76; str | None = None; optional, default None; no alias or deprecation; M0 / META has exact /info/description selectors.
- fastapi.openapi.models.Info.termsOfService — models.py:77; str | None = None; optional, default None; no alias or deprecation; M0 / META has exact /info/termsOfService selectors. Its annotation is str, not AnyUrl.
- fastapi.openapi.models.Info.contact — models.py:78; Contact | None = None; optional, default None; no alias or deprecation; M0 / META selects /info/contact as an object, not Contact field leaves.
- fastapi.openapi.models.Info.license — models.py:79; License | None = None; optional, default None; no alias or deprecation; M0 / META selects /info/license as an object, not License field leaves.
- fastapi.openapi.models.Info.version — models.py:80; str, required, no default; no alias or deprecation; M0 / META has an exact /info/version selector in docs-reference-openapi.yaml.
- fastapi.openapi.models.License — class models.py:67; reflected keyword-only signature as listed above; M0 / META. No direct License constructor or identity input.
- fastapi.openapi.models.License.name — models.py:68; str, required, no default; no alias or deprecation; M0 / META selects the containing /info/license object only.
- fastapi.openapi.models.License.identifier — models.py:69; str | None = None; optional, default None; no alias or deprecation; M0 / META selects the containing object only. The application docs describe identifier as an SPDX expression and mutually exclusive with url, but models.py declares neither a mutual-exclusion validator nor a Field constraint for these fields.
- fastapi.openapi.models.License.url — models.py:70; AnyUrl | None = None; optional, default None; no alias or explicit Field constraint; M0 / META selects the containing object only.

### Security base, scheme alias, HTTP models, OAuth flows, and OpenID Connect

- fastapi.openapi.models.SecuritySchemeType — Enum class models.py:321; reflected runtime signature has variadic positional values; M1. Exact member values are listed below.
- fastapi.openapi.models.SecuritySchemeType.apiKey — models.py:322; Enum value "apiKey"; M1, the only enum member with a partial reviewed operation mapping.
- fastapi.openapi.models.SecuritySchemeType.http — models.py:323; Enum value "http"; M0 / HTTP observes selected emitted security schemes, not direct Enum member identity.
- fastapi.openapi.models.SecuritySchemeType.oauth2 — models.py:324; Enum value "oauth2"; M0 / OAUTH observes selected emitted security schemes, not direct Enum member identity.
- fastapi.openapi.models.SecuritySchemeType.openIdConnect — models.py:325; Enum value "openIdConnect"; M0 / OPENID observes selected emitted security schemes, not direct Enum member identity.
- fastapi.openapi.models.SecurityBase — class models.py:328; inherits BaseModelWithConfig; reflected keyword-only signature has required parameter type (field type_) and optional description, followed by **extra_data: Any; M1.
- fastapi.openapi.models.SecurityBase.type_ — models.py:329; SecuritySchemeType = Field(alias="type"); required with no default; wire/model alias "type"; M1. Generated OpenAPI output uses aliases, but this does not test Python-name versus alias input.
- fastapi.openapi.models.SecurityBase.description — models.py:330; str | None = None; optional, default None; no alias, explicit constraint, or deprecation; M1.
- fastapi.openapi.models.SecurityScheme — union type alias at models.py:396: APIKey | HTTPBase | OAuth2 | OpenIdConnect | HTTPBearer. It is the type used by Components.securitySchemes together with Reference at models.py:406; there is no Pydantic model constructor signature, class binding, or direct alias-identity workflow. M0 / SEC.
- fastapi.openapi.models.HTTPBase — class models.py:345, subclass of SecurityBase; reflected signature includes inherited type (default SecuritySchemeType.http), description=None, required scheme, then **extra_data: Any; M0 / HTTP. Direct model construction and identity are gaps.
- fastapi.openapi.models.HTTPBase.type_ — models.py:346; SecuritySchemeType = Field(default=SecuritySchemeType.http, alias="type"); optional with enum default; alias "type"; M0 / HTTP selects type in generated security documents, not direct field validation.
- fastapi.openapi.models.HTTPBase.scheme — models.py:347; str, required, no default; no alias, explicit constraint, or deprecation; M0 / HTTP selects scheme in generated security documents, not direct field validation.
- fastapi.openapi.models.HTTPBearer — class models.py:350, subclass of HTTPBase; reflected signature includes inherited type and description plus scheme and bearerFormat, then **extra_data: Any; M0 / HTTP. Its inherited type_ candidate is HTTPBase.type_, not a separate HTTPBearer.type_ candidate.
- fastapi.openapi.models.HTTPBearer.scheme — models.py:351; Literal["bearer"] = "bearer"; optional with literal default; no alias or deprecation; M0 / HTTP selects scheme in generated documents. No invalid-literal constructor/validation case.
- fastapi.openapi.models.HTTPBearer.bearerFormat — models.py:352; str | None = None; optional, default None; no alias, explicit constraint, or deprecation; M0. No active recipe pointer for bearerFormat.
- fastapi.openapi.models.OAuth2 — class models.py:384, subclass of SecurityBase; reflected signature includes type default SecuritySchemeType.oauth2, inherited description=None, required flows, then **extra_data: Any; M0 / OAUTH.
- fastapi.openapi.models.OAuth2.type_ — models.py:385; SecuritySchemeType = Field(default=SecuritySchemeType.oauth2, alias="type"); optional with enum default; alias "type"; M0 / OAUTH selects emitted type values.
- fastapi.openapi.models.OAuth2.flows — models.py:386; OAuthFlows, required, no default; no alias or deprecation; M0 / OAUTH observes nested selected flow members, not direct flows construction.
- fastapi.openapi.models.OAuthFlow — class models.py:355; reflected signature has refreshUrl=None and scopes={}, then **extra_data: Any; M0 / OAUTH. No direct model constructor or identity input.
- fastapi.openapi.models.OAuthFlow.refreshUrl — models.py:356; str | None = None; optional, default None; no alias or deprecation; M0. No active recipe pointer for refreshUrl.
- fastapi.openapi.models.OAuthFlow.scopes — models.py:357; dict[str, str] = {}; default empty dict; no alias, explicit Field constraint, or deprecation; M0 / OAUTH selects password and authorization-code scope maps in some recipes. The declaration is the source fact; Pydantic owns runtime default-copy and validation behavior.
- fastapi.openapi.models.OAuthFlowAuthorizationCode — class models.py:372, subclass of OAuthFlow; reflected signature includes inherited refreshUrl/scopes and required authorizationUrl/tokenUrl, then **extra_data: Any; M0 / OAUTH.
- fastapi.openapi.models.OAuthFlowAuthorizationCode.authorizationUrl — models.py:373; str, required, no default; no alias or deprecation; M0 / OAUTH has an exact authorizationCode/authorizationUrl output selector.
- fastapi.openapi.models.OAuthFlowAuthorizationCode.tokenUrl — models.py:374; str, required, no default; no alias or deprecation; M0 / OAUTH has an exact authorizationCode/tokenUrl output selector.
- fastapi.openapi.models.OAuthFlowClientCredentials — class models.py:368, subclass of OAuthFlow; reflected signature includes inherited refreshUrl/scopes and required tokenUrl, then **extra_data: Any; M0. No active clientCredentials-flow pointer.
- fastapi.openapi.models.OAuthFlowClientCredentials.tokenUrl — models.py:369; str, required, no default; no alias or deprecation; M0. No active clientCredentials-flow pointer.
- fastapi.openapi.models.OAuthFlowImplicit — class models.py:360, subclass of OAuthFlow; reflected signature includes inherited refreshUrl/scopes and required authorizationUrl, then **extra_data: Any; M0. No active implicit-flow pointer.
- fastapi.openapi.models.OAuthFlowImplicit.authorizationUrl — models.py:361; str, required, no default; no alias or deprecation; M0. No active implicit-flow pointer.
- fastapi.openapi.models.OAuthFlowPassword — class models.py:364, subclass of OAuthFlow; reflected signature includes inherited refreshUrl/scopes and required tokenUrl, then **extra_data: Any; M0 / OAUTH.
- fastapi.openapi.models.OAuthFlowPassword.tokenUrl — models.py:365; str, required, no default; no alias or deprecation; M0 / OAUTH has exact password/tokenUrl output selectors.
- fastapi.openapi.models.OAuthFlows — class models.py:377; reflected signature has all four flow fields defaulting to None, then **extra_data: Any; M0 / OAUTH. No direct OAuthFlows construction or identity input.
- fastapi.openapi.models.OAuthFlows.implicit — models.py:378; OAuthFlowImplicit | None = None; optional, default None; no alias or deprecation; M0. No active implicit-flow pointer.
- fastapi.openapi.models.OAuthFlows.password — models.py:379; OAuthFlowPassword | None = None; optional, default None; no alias or deprecation; M0 / OAUTH observes nested password flow properties.
- fastapi.openapi.models.OAuthFlows.clientCredentials — models.py:380; OAuthFlowClientCredentials | None = None; optional, default None; no alias or deprecation; M0. No active clientCredentials-flow pointer.
- fastapi.openapi.models.OAuthFlows.authorizationCode — models.py:381; OAuthFlowAuthorizationCode | None = None; optional, default None; no alias or deprecation; M0 / OAUTH observes nested authorization-code flow properties.
- fastapi.openapi.models.OpenIdConnect — class models.py:389, subclass of SecurityBase; reflected signature includes type default SecuritySchemeType.openIdConnect, inherited description=None, required openIdConnectUrl, then **extra_data: Any; M0 / OPENID.
- fastapi.openapi.models.OpenIdConnect.type_ — models.py:390-392; SecuritySchemeType = Field(default=SecuritySchemeType.openIdConnect, alias="type"); optional with enum default; alias "type"; M0 / OPENID selects emitted type.
- fastapi.openapi.models.OpenIdConnect.openIdConnectUrl — models.py:393; str, required, no default; no alias or deprecation; M0 / OPENID selects this value in emitted security documents. The annotation is str, not AnyUrl.

## FastAPI call chain

### Info and metadata

- FastAPI.__init__ exposes title, summary, description, version, terms_of_service, contact, and license_info and stores them on the application object. The application OpenAPI call at applications.py:1086-1100 passes these attributes to get_openapi.
- openapi/utils.py:585-601 declares get_openapi. It always seeds the Info input dictionary with title and version at line 602, adds summary, description, termsOfService, contact, and license only when each input is truthy at lines 603-612, and places that dictionary under root info at line 613.
- get_openapi then creates the OpenAPI model at utils.py:679 and encodes by_alias=True and exclude_none=True. The normal application route therefore exercises nested Info/Contact/License objects as generated-document projections. It does not by itself establish direct class import, constructor, alias-input, field-validation, or identity behavior.

### Security and OAuth

- fastapi/security/http.py imports HTTPBase and HTTPBearer model aliases from fastapi.openapi.models at lines 7-8. HTTPBase.__init__ constructs HTTPBaseModel(scheme=..., description=...) at lines 69-82; HTTPBearer.__init__ constructs HTTPBearerModel at lines 254-301.
- fastapi/security/oauth2.py imports OAuth2 and OAuthFlows model aliases at lines 5-6. OAuth2.__init__ constructs OAuth2Model from the flow configuration and description at lines 343-399. OAuth2PasswordBearer builds the password flow model at lines 442-534; OAuth2AuthorizationCodeBearer builds the authorization-code flow model at lines 547-640.
- fastapi/security/open_id_connect_url.py imports OpenIdConnect as its model alias at line 4 and creates the model at lines 22-78. Its source describes the dependency class as a stub connection to the OpenAPI scheme; it does not implement the full OpenID Connect protocol.
- openapi/utils.py:132-156 takes each security dependency's .model, calls jsonable_encoder with by_alias=True and exclude_none=True, keys the security definition by scheme_name, and builds operation security scope maps. get_openapi_path calls this flow at lines 348-356. get_openapi inserts resulting security schemes under components at lines 639-645, then constructs/encodes the root OpenAPI model at line 679.
- The operation-security recipe outputs are observations of these constructed dictionaries and the final document. They are not direct constructor, class-identity, or Pydantic validation tests.

## Existing recipe and selector evidence

These are input-only recipes. They contain no expected outputs and no result is claimed here.

- Documentation design for all 54 candidates: manifest documentation fixture fastapi.docs.reference-openapi-models, mapping_status candidate, selectors python.import_path, python.signature, python.attribute_value, and openapi.document. This is a design link, not a materialized input workflow.
- Direct class signature probe: direct-api-reference-wave.yaml, case fastapi.direct-api-reference-wave.openapi-info-signature, selector python.signature. The manifest attaches this input only to fastapi.openapi.models.Info.
- Metadata recipe: metadata-summary-description-upstream.yaml, case fastapi.metadata.summary-description.openapi-info, selects /info/summary, /info/description, /info/termsOfService, /info/contact, and /info/license. metadata-tutorial001-upstream.yaml, case fastapi.docs.metadata.tutorial001.openapi-info-fields, selects the same set. These select Contact and License objects but not their name/url/email or name/identifier/url leaves. metadata-tutorial001-1-upstream.yaml, case fastapi.test.test-tutorial-test-metadata-test-tutorial001-1.test-openapi-schema, selects /info/license as a whole. docs-reference-openapi.yaml, case fastapi.docs.reference-wave.openapi.fastapi-application-settings, selects /info/title, /info/summary, and /info/version. Numerous other recipes select /info as a whole; that is document-level scope, not direct nested-model coverage.
- SecurityBase and partial target slice: manifest operation_fixture_refs for fastapi.openapi.models.SecurityBase, .description, .type_, SecuritySchemeType, and SecuritySchemeType.apiKey refer to eight cases: seven cases in security_credentials_upstream (api-key-cookie, api-key-cookie-optional, api-key-cookie-description, api-key-query, api-key-query-optional, api-key-query-description, and api-key-header-description, each with test-openapi-schema case ID) plus security-api-key-header-openapi / fastapi.test.security-api-key-header.default-name-openapi. Their manifest selectors are openapi.document and openapi.security (the latter where present). They observe API-key scheme construction; they do not test these model types directly.
- HTTP generated-security evidence: http-basic.yaml / fastapi.advanced.security.http-basic.openapi selects HTTPBasic type, scheme, and operation security. security_credentials_upstream.yaml has HTTP base/bearer cases, including fastapi.security.http-base-optional.test-openapi-schema and fastapi.security.http-bearer.test-openapi-schema, with selected type/scheme leaves. security-atlas-wave.yaml / fastapi.security-atlas-wave.http-bearer-description.default-name-openapi selects a complete emitted HTTPBearer scheme object and operation security. No active selector was found for HTTPBearer.bearerFormat.
- OAuth password and generic flows: security_oauth_openapi_upstream.yaml cases fastapi.security.oauth2-password-bearer-optional-description.test-openapi-schema and fastapi.security.oauth2-optional-description.test-openapi-schema select type, password/tokenUrl, description, and operation security. Scope selectors appear in security_oauth_openapi_upstream.yaml, security-dependencies.yaml, security-tutorial005-auth-scopes-gap-wave.yaml, security-scopes-dont-propagate-openapi-source-review.yaml, docs-reference-http.yaml, and docs-dependencies-security.yaml. These include password scope maps and authorizationCode read/write scope leaves.
- OAuth authorization-code fields: security_oauth_openapi_upstream.yaml / fastapi.security.oauth2-authorization-code-bearer.test-openapi-schema selects /flows/authorizationCode/authorizationUrl and /tokenUrl; its scopes case selects /flows/authorizationCode/scopes/read and /write. There is no direct flow model constructor or identity case.
- OAuth flow gaps: no explicit JSON-pointer selector was found for refreshUrl, implicit, or clientCredentials. Current generated-document coverage of password and authorizationCode leaves does not cover those alternatives or direct OAuthFlows construction.
- OpenID Connect: security_oauth_openapi_upstream.yaml cases fastapi.security.openid-connect.test-openapi-schema, fastapi.security.openid-connect-description.test-openapi-schema, and fastapi.security.openid-connect-optional.test-openapi-schema select the type, openIdConnectUrl, and (for the described case) description. security-atlas-wave.yaml / fastapi.security-atlas-wave.openid-connect-description.default-name-openapi also selects the whole OpenIdConnect scheme and operation security. These are generated-document cases, not direct model identity or validation workflows.

## Current target manifest and facade state

The active target manifest is tests/fixtures/manifest.yaml; atlas classifications are from tests/fixtures/compatibility-atlas.json; metadata.yaml owns reviewed operation overlays.

- Every one of the 54 candidate symbols has source_signature_state not-recorded and the same candidate documentation design reference described above. All 15 model/enum classes have signature_contract_state runtime-signature-reflected; 38 field/member candidates and the SecurityScheme union value have non-callable-surface. Those records do not by themselves establish input workflow or parity.
- Forty-eight IDs have the M0 state. fastapi.openapi.models.Info is MI: operation remains scope-review-pending and Rust binding is null, with only the direct signature input above. It has no identity workflow.
- The other five IDs are M1: fastapi.openapi.models.SecurityBase, SecurityBase.description, SecurityBase.type_, SecuritySchemeType, and SecuritySchemeType.apiKey. Each is slice-described and has rust_binding fastapi-rs/src/security.rs::create_api_key_models; each remains full-contract-not-established. The existing API-key operation fixtures do not establish direct model import/identity, exact Python-name versus alias behavior, model validation, constructor signature parity, or full security scheme coverage.
- All 54 identity_workflow_refs are empty. The group has no alias_refs or deprecation_refs in the manifest. The 49 pending operation scopes include every candidate except the five listed M1 IDs.
- fastapi-rs-py/python/fastapi/openapi/models.py currently re-exports APIKey, APIKeyIn, BaseModelWithConfig, SecuritySchemeType, and SecurityBase from fastapi_rs._core. Within this review group, only SecuritySchemeType and SecurityBase are named in that file. The rest of the reviewed candidate names have no Rust binding in the active manifest. Re-export visibility and the M1 slice do not imply a complete model contract.
- The broader security recipes provide partial emitted-document coverage for APIKey, HTTP, OAuth2, and OpenIdConnect schemes, while direct class imports, model constructors, nested Pydantic errors, aliases, omitted-versus-null behavior, extra fields, and complete flow alternatives remain outside the described target slice. No parity conclusion follows from this draft.

No tests or benchmarks were run. The only new file from this review is this draft.
