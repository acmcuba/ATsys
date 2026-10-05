#include <openssl/evp.h>
#include <openssl/pem.h>

#include <stdio.h>
#include <string.h>

enum {
    RCC_OK = 0,
    RCC_USAGE_ERROR = 2,
    RCC_FSSW_SIZE_ERROR = 3,
    RCC_SIGNATURE_SIZE_ERROR = 4,
    RCC_PUBLIC_KEY_ERROR = 5,
    RCC_CRYPTO_ERROR = 6,
    RCC_SIGNATURE_REJECTED = 10
};

#define RCC_FSSW_BYTES 128U
#define RCC_ED25519_SIGNATURE_BYTES 64U

static int read_exact_file(
    const char *path,
    unsigned char *buffer,
    size_t expected_size)
{
    FILE *stream;
    size_t bytes_read;
    int trailing_byte;

    stream = fopen(path, "rb");
    if (stream == NULL) {
        return -1;
    }

    bytes_read = fread(buffer, 1U, expected_size, stream);

    if (ferror(stream) != 0) {
        fclose(stream);
        return -1;
    }

    trailing_byte = fgetc(stream);

    if (fclose(stream) != 0) {
        return -1;
    }

    if (bytes_read != expected_size || trailing_byte != EOF) {
        return 0;
    }

    return 1;
}

static EVP_PKEY *load_ed25519_public_key(const char *path)
{
    FILE *stream;
    EVP_PKEY *public_key;

    stream = fopen(path, "rb");
    if (stream == NULL) {
        return NULL;
    }

    public_key = PEM_read_PUBKEY(stream, NULL, NULL, NULL);
    fclose(stream);

    if (public_key == NULL) {
        return NULL;
    }

    if (EVP_PKEY_is_a(public_key, "ED25519") != 1) {
        EVP_PKEY_free(public_key);
        return NULL;
    }

    return public_key;
}

int main(int argc, char **argv)
{
    unsigned char fssw[RCC_FSSW_BYTES];
    unsigned char signature[RCC_ED25519_SIGNATURE_BYTES];
    EVP_PKEY *public_key = NULL;
    EVP_MD_CTX *context = NULL;
    int read_result;
    int verify_result;
    int exit_code = RCC_CRYPTO_ERROR;

    if (argc != 4) {
        fprintf(
            stderr,
            "USAGE=%s PUBLIC_KEY_PEM FSSW_128 SIGNATURE_64\n",
            argv[0]);
        return RCC_USAGE_ERROR;
    }

    read_result = read_exact_file(
        argv[2], fssw, sizeof(fssw));

    if (read_result != 1) {
        fprintf(stderr, "FSSW_SIZE_VALID=NO\n");
        return RCC_FSSW_SIZE_ERROR;
    }

    read_result = read_exact_file(
        argv[3], signature, sizeof(signature));

    if (read_result != 1) {
        fprintf(stderr, "SIGNATURE_SIZE_VALID=NO\n");
        return RCC_SIGNATURE_SIZE_ERROR;
    }

    public_key = load_ed25519_public_key(argv[1]);
    if (public_key == NULL) {
        fprintf(stderr, "PUBLIC_KEY_VALID=NO\n");
        return RCC_PUBLIC_KEY_ERROR;
    }

    context = EVP_MD_CTX_new();
    if (context == NULL) {
        fprintf(stderr, "CRYPTO_CONTEXT=FAIL\n");
        EVP_PKEY_free(public_key);
        return RCC_CRYPTO_ERROR;
    }

    if (EVP_DigestVerifyInit(
            context, NULL, NULL, NULL, public_key) != 1) {
        fprintf(stderr, "VERIFY_INIT=FAIL\n");
        goto cleanup;
    }

    verify_result = EVP_DigestVerify(
        context,
        signature,
        sizeof(signature),
        fssw,
        sizeof(fssw));

    if (verify_result == 1) {
        printf("ALGORITHM=ED25519\n");
        printf("FSSW_SIZE=128\n");
        printf("SIGNATURE_SIZE=64\n");
        printf("CRYPTOGRAPHIC_VERIFICATION=PASS\n");
        printf("RESULT=PASS\n");
        exit_code = RCC_OK;
    } else if (verify_result == 0) {
        printf("ALGORITHM=ED25519\n");
        printf("CRYPTOGRAPHIC_VERIFICATION=REJECTED\n");
        printf("RESULT=REJECTED\n");
        exit_code = RCC_SIGNATURE_REJECTED;
    } else {
        fprintf(stderr, "VERIFY_OPERATION=ERROR\n");
        exit_code = RCC_CRYPTO_ERROR;
    }

cleanup:
    EVP_MD_CTX_free(context);
    EVP_PKEY_free(public_key);
    return exit_code;
}
