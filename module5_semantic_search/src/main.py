from document_loader import load_documents


def main():

    documents = load_documents()

    print(f"Loaded {len(documents)} documents.\n")

    print(documents[0])


if __name__ == "__main__":
    main()