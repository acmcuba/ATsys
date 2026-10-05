# RCC-FSSW-CRYPTO-V00.1

## Detached Ed25519 Verification of an Experimental FSSW

**Project:** ATsys ARE RCC  
**Experiment:** RCC-FSSW-CRYPTO-V00.1-DETACHED-ED25519  
**Experimental node:** edgenode003  
**Experimental closure:** 2026-09-21 18:37:19 UTC  
**Status:** PASS / FROZEN  
**Canonical:** NO  
**Generalizable:** NO  
**RCM promotion:** NONE  
**Operational authority:** NONE  

---

## 1. Experimental Question

Can a deterministic C verifier authenticate a 128-byte experimental
FSSW using a detached Ed25519 signature, accept the intact object,
reject changes to the object, signature, and public key, and enforce
the exact structural sizes without modifying the FSSW contract or
the resident RCM object?

---

## 2. What Was Demonstrated

RCC-FSSW-CRYPTO-V00.1 demonstrated detached Ed25519 verification of
one 128-byte experimental FSSW resident in the RCM Cloud anchored at
edgenode003.

OpenSSL was used as an external verification oracle. A C verifier
using the OpenSSL EVP interface reproduced the same acceptance and
rejection decisions for the tested cases.

The experiment demonstrated:

- successful verification of the intact FSSW;
- rejection of an altered FSSW;
- rejection of an altered detached signature;
- rejection under a different Ed25519 public key;
- rejection of 127-byte and 129-byte FSSW inputs;
- rejection of 63-byte and 65-byte signatures;
- agreement between the C verifier and the OpenSSL oracle;
- preservation of the original resident RCM object;
- preservation of the 1024-bit FSSW binary contract.

The experiment closed with:

`RESULT=PASS`

---

## 3. Realization

The experimental realization uses:

- FSSW size: 128 bytes / 1024 bits
- detached signature size: 64 bytes
- signature algorithm: Ed25519
- C implementation
- OpenSSL EVP verification backend
- fixed structural guards for FSSW and signature size

The verifier implementation is available at:

`src/rcc_fssw_ed25519_verify.c`

The implementation is intentionally narrow. It performs cryptographic
verification only and does not grant trust, admission, promotion,
authorization, or operational authority.

---

## 4. Experimental Result

Four experimental runs closed with PASS:

| Run | Purpose | Result |
|---|---|---|
| RUN-01 | OpenSSL positive verification | PASS |
| RUN-02 | Cryptographic negative controls | PASS |
| RUN-03 | C verifier / OpenSSL decision agreement | PASS |
| RUN-04 | Structural size guards | PASS |

The compact experimental closure record is available at:

`evidence/FINAL_RESULT.txt`

---

## 5. Demonstrated Scope

The demonstrated scope is intentionally limited to:

> Detached Ed25519 verification of one 128-byte experimental FSSW
> resident in the RCM Cloud anchored at edgenode003.

This is an experimental result.

It is not presented as a canonical or general RCC security mechanism.

---

## 6. What Was NOT Demonstrated

V00.1 does not demonstrate:

- signer identity trust;
- key lifecycle management;
- key revocation;
- multinode trust;
- automatic RCM admission;
- RCM promotion;
- operational authorization;
- confidentiality;
- availability;
- remote attestation;
- secure key storage;
- or a malloc-free cryptographic RCC core.

A mathematically valid signature must not be interpreted by this
experiment as proof that a signer is trusted or that an object is
authorized to perform an operation.

---

## 7. Public Evidence

This public knowledge unit intentionally contains a minimal evidence
set rather than the complete internal experimental workspace.

### Public report

`report/RCC_FSSW_CRYPTO_V00_1_Public_Release_2026_10_05.docx`

SHA-256:

`125717691a87c8c6858db8f14ae8e3ca4cbaf8933711a10118ff90b01ab87b4d`

### C verifier

`src/rcc_fssw_ed25519_verify.c`

SHA-256:

`23378201e76fd5a8bd7e6a5cfe418f3548983d6077997b29919e6153037206a8`

### Experimental closure

`evidence/FINAL_RESULT.txt`

SHA-256:

`b67176398a2fda9975fa090ef6720315ca5c045157492750d470eb9448c89ce1`

---

## 8. Source Object Identity

Experimental FSSW:

`SOE-V00.1_FSSW_0x534F4501`

FSSW identifier:

`0x534F4501`

Size:

`128 bytes`

SHA-256:

`45cb1a7ef41a86e1463beabbaff64efd2aa6c5fab09025e1d6538f6dd1e8b06b`

The experimental record reports:

`SOURCE_COPY_BYTE_IDENTITY=PASS`

and:

`ORIGINAL_RCM_OBJECT_UNCHANGED=PASS`

---

## 9. Public Release Boundary

This repository directory is a controlled public projection of the
experimental closure.

The original experimental record remains preserved separately and
unchanged.

Prospective architecture and later experimental directions are not
part of this public release and remain subject to separate technical
and intellectual-property review.

Private cryptographic keys are explicitly excluded from this public
unit.

This publication boundary is not a statement about patentability,
novelty, canonical status, or generalizability.

---

## 10. Knowledge Closure

The public unit represents the following closed experimental relation:

**Question -> Realization -> Verification -> Evidence -> Result -> Limits**

For V00.1:

**Experimental question**  
-> detached Ed25519 realization  
-> OpenSSL oracle + C verifier  
-> positive, negative, and structural tests  
-> reproducible PASS  
-> explicitly bounded claims

Future work does not modify or reinterpret this closure.

---

## 11. Genealogy

**V00.1:** experimental cryptographic verification baseline — PASS / FROZEN.

Later work belongs to a separate genealogical branch and is not
described by this public unit.

---

## Scientific Status

**OBSERVED / DEMONSTRATED:** YES  
**EXPERIMENTAL PASS:** YES  
**FROZEN BASELINE:** YES  
**CANONICAL:** NO  
**GENERALIZABLE:** NO  
**AUTOMATIC AUTHORITY:** NO
