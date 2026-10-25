# Phase 1C locked dependencies

[Machine manifest and exact lock hashes](dependency-manifest.json) record runtime/dev pins. `package-lock.json` and `uv.lock` retain transitive versions and package integrity hashes; all previous direct pins remain. Pillow 13.0.0 is added for bounded pixel decoding/sanitization. No recognition model or provider is installed.

| Component | Pin / evidence |
|---|---|
| Node / npm | 24.18.0 / 11.16.0 |
| Python / uv | 3.13.13 / 0.12.0 |
| TesterArmy / web / Playwright core | 0.21.3 / 0.15.3 / 1.64.1; reviewed repository `69e123b17e04ed624df16d32f3b1ef95ce22c083` |
| Next / React / TypeScript | 16.4.3 / 19.3.1 / 7.0.2 |
| PostgreSQL / vector / Keycloak | Existing 17.11 / 0.8.7 / 26.7.0 and approved OCI digests preserved in compose |
| Image decoder | Pillow 13.0.0 |
| Scanner | Official ClamAV Debian 1.5.4, multi-arch OCI digest in manifest |
| Private S3 development server | SeaweedFS 4.48, OCI digest in manifest |

Primary implementation references: [ClamAV official Docker documentation](https://docs.clamav.net/manual/Installing/Docker.html), [ClamAV 1.5.4 release](https://github.com/Cisco-Talos/clamav/releases/tag/clamav-1.5.4), [Pillow 13.0.0 release](https://pillow.readthedocs.io/en/stable/releasenotes/13.0.0.html), [Pillow image security](https://pillow.readthedocs.io/en/stable/handbook/security.html), [SeaweedFS 4.48 source/release](https://github.com/seaweedfs/seaweedfs/releases/tag/4.48), [official S3 configuration](https://github.com/seaweedfs/seaweedfs/blob/4.48/weed/command/s3.go), and the preserved [TesterArmy integration evidence](../E2E_FRAMEWORK_INTEGRATION.md). No upstream README or version pin is treated as application execution evidence.

The Alpine scanner image lacked ARM64 support on this Mac; the official Debian multi-arch image was verified and used. Runtime networks remain private; scanner signature updates are disabled in the reproducible test snapshot. Operational signature freshness, SBOM/license/vendor approval and production KMS/hosting remain release gates. Apache-2.0 storage, GPL scanner and Pillow licensing require the normal project license review; no model license is inferred.
