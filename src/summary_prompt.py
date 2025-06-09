def get_prompt():

    return """**Objective:** Analyze the provided document to produce a clear summary that includes all key points and their locations (page numbers). The output should be structured to facilitate the easy creation of a knowledge graph or conceptual map with source attribution.

        **Document Text:**
        Section Name
        --------------------
        {section_name}

        Text
        -------------------
        {text_contents}

        **Instructions:**

        Please analyze the document and provide the following information in a structured format:

        1.  **Overall Document Summary:**
            *   A concise summary (3-5 sentences) that clearly captures the main purpose, core arguments, and overall conclusions of the document.

        2.  **Key Entities/Concepts (Nodes):**
            *   Identify and list the most important entities, concepts, organizations, individuals, processes, or items discussed. These will serve as the primary nodes in a graph.
            *   For each entity/concept, provide a brief (1-sentence) description of its role or significance within the document and the page number(s) where it is prominently mentioned or defined.
            *   **Format:**
                *   **Entity/Concept:** [Name of Entity/Concept 1]
                    *   **Description:** [Brief description of its role/significance]
                    *   **Page Number(s):** [e.g., 5, 12-14]
                *   **Entity/Concept:** [Name of Entity/Concept 2]
                    *   **Description:** [Brief description of its role/significance]
                    *   **Page Number(s):** [e.g., 3, 8]
                *   ... (List all significant entities/concepts)

        3.  **Key Relationships/Interactions (Edges):**
            *   Describe the significant relationships, interactions, dependencies, influences, or actions between the identified key entities/concepts. These will form the edges in a graph.
            *   Clearly state the source entity/concept, the target entity/concept, the nature of their relationship, and the page number(s) where this relationship is described or evidenced.
            *   **Format:**
                *   **Relationship:** `[Source Entity/Concept]` --([Nature of Relationship, e.g., "influences", "is part of", "regulates", "proposes", "challenges"])--&gt; `[Target Entity/Concept]`
                    *   **Context/Details:** [Optional: A brief explanation or key detail about this specific relationship as found in the document]
                    *   **Page Number(s):** [e.g., 7, 10]
                *   ... (List all significant relationships)

        4.  **Main Themes/Information Clusters:**
            *   Group related key points, findings, or arguments from the document into distinct themes or information clusters. This helps in understanding the document's structure and can represent higher-level concepts or contexts in a graph.
            *   For each theme/cluster:
                *   Provide a clear title for the theme/cluster.
                *   Write a brief summary (2-3 sentences) of the main information or key points contained within this theme/cluster.
                *   List the primary entities/concepts (from section 2) that are central to this theme/cluster.
            *   **Format:**
                *   **Theme/Cluster Title:** [Title of Theme/Cluster 1]
                    *   **Summary:** [Brief summary of this theme/cluster and its key points]
                    *   **Central Entities/Concepts:** [List of relevant entities/concepts]
                *   **Theme/Cluster Title:** [Title of Theme/Cluster 2]
                    *   **Summary:** [Brief summary of this theme/cluster and its key points]
                    *   **Central Entities/Concepts:** [List of relevant entities/concepts]
                *   ... (List all major themes/clusters)

        **Output Guidelines:**
        *   Adhere strictly to the headings and formatting provided above.
        *   Ensure all significant key points from the document are captured within the overall summary, the descriptions of entities/relationships, or the summaries of themes/clusters.
        *   Include page numbers for entities/concepts and relationships where this information is available and relevant from the source document. If a concept or relationship spans multiple pages, indicate the range or key pages.
        *   The language should be clear and precise, using terminology from the document where appropriate.
        *   The ultimate goal is a structured output that not only summarizes the document but also explicitly maps out its core components, their interconnections, and their source locations, making it readily usable for graph construction and verification.
    """