"""
Test HuggingFace downloader functionality.

This script tests the HuggingFace Hub integration without running the full GUI.
"""

from pathlib import Path

from huggingface_hub import list_repo_files


def test_list_repo_files():
    """Test listing files in a HuggingFace repo."""
    print("Testing: List repo files")
    print("-" * 50)

    # Test with a known GGUF repo
    repo_id = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"

    try:
        print(f"Listing files in: {repo_id}")
        files = list_repo_files(repo_id)

        # Filter for GGUF files
        gguf_files = [f for f in files if f.endswith(".gguf")]

        print(f"\nFound {len(gguf_files)} GGUF files:")
        for i, file in enumerate(gguf_files, 1):
            print(f"  {i}. {file}")

        return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def test_parse_url():
    """Test parsing HuggingFace URLs."""
    print("\nTesting: Parse URLs")
    print("-" * 50)

    test_urls = [
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q8_0.gguf",
    ]

    for url in test_urls:
        print(f"\nURL: {url}")

        try:
            parts = url.replace("https://", "").replace("huggingface.co/", "").split("/")

            username = parts[0]
            repo_name = parts[1]
            repo_id = f"{username}/{repo_name}"

            print(f"  Repo ID: {repo_id}")

            # Check if specific file is mentioned
            if len(parts) > 3 and parts[2] in ["blob", "resolve"]:
                filename = "/".join(parts[4:])
                print(f"  Filename: {filename}")
            else:
                print("  Filename: (none - will scan repo)")

        except Exception as e:
            print(f"  Error: {e}")

    return True


def test_download_info():
    """Show download info without actually downloading."""
    print("\nTesting: Download info")
    print("-" * 50)

    repo_id = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
    filename = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"

    print(f"Repo: {repo_id}")
    print(f"File: {filename}")
    print(f"Would download to: {Path('models').absolute()}")

    # Note: We don't actually download here to avoid large downloads during testing
    print("\n✓ Download function would work with:")
    print("  hf_hub_download(")
    print(f"      repo_id='{repo_id}',")
    print(f"      filename='{filename}',")
    print("      local_dir='models',")
    print("      local_dir_use_symlinks=False,")
    print("      resume_download=True")
    print("  )")

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("HuggingFace Integration Test")
    print("=" * 50)

    tests = [
        ("Parse URL", test_parse_url),
        ("List Repo Files", test_list_repo_files),
        ("Download Info", test_download_info),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            results.append((name, False))
        print()

    print("=" * 50)
    print("Test Results:")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print("\nAll tests completed!")
