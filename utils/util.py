def format_docs(docs):
        """
        Formatting retrieval output

        Args:
            docs (List[Document]): retrieval outputs

        Returns:
            str: concat retrieved places
        """
        return "\n".join(doc.metadata["name"] for doc in docs)