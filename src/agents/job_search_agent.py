from typing import Any

from langchain_core.messages import AIMessage
from langchain_tavily import TavilySearch

from src.config import settings


# =========================================================
# TAVILY SEARCH
# =========================================================

tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="basic",
    tavily_api_key=settings.TAVILY_API_KEY,
)


# =========================================================
# JOB SEARCH AGENT
# =========================================================

class JobSearchAgent:
    """
    Direct Tavily job-search agent.

    We intentionally DO NOT use create_react_agent()
    here.

    Why?

    GPT-OSS was previously trying to call unavailable tools
    such as "open_file", causing:

        Tool call validation failed

    Tavily is now called directly, which makes the search
    pipeline much more reliable and predictable.
    """

    def invoke(
        self,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:

        messages = input_data.get(
            "messages",
            []
        )

        if not messages:
            return {
                "messages": [
                    AIMessage(
                        content=""
                    )
                ]
            }

        last_message = messages[-1]

        if isinstance(last_message, dict):

            query_text = str(
                last_message.get(
                    "content",
                    ""
                )
            )

        else:

            query_text = str(
                getattr(
                    last_message,
                    "content",
                    last_message,
                )
            )

        # -------------------------------------------------
        # Extract queries
        # -------------------------------------------------

        queries = self._extract_queries(
            query_text
        )

        if not queries:

            queries = [
                query_text[:400]
            ]

        # Maximum 4 searches
        queries = queries[:4]

        print(
            f"  → Running {len(queries)} Tavily searches..."
        )

        all_results = []

        # -------------------------------------------------
        # Run Tavily searches
        # -------------------------------------------------

        for index, query in enumerate(
            queries,
            start=1,
        ):

            query = query.strip()

            if not query:
                continue

            print(
                f"  → Search {index}: {query}"
            )

            try:

                result = tavily_search.invoke(
                    {
                        "query": query
                    }
                )

            except Exception as exc:

                print(
                    f"  ⚠ Search failed: {exc}"
                )

                continue

            if not isinstance(
                result,
                dict,
            ):
                continue

            results = result.get(
                "results",
                []
            )

            if not isinstance(
                results,
                list,
            ):
                continue

            for item in results:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                title = str(
                    item.get(
                        "title",
                        ""
                    )
                ).strip()

                url = str(
                    item.get(
                        "url",
                        ""
                    )
                ).strip()

                content = str(
                    item.get(
                        "content",
                        ""
                    )
                ).strip()

                if not url:
                    continue

                # Compress snippet aggressively
                content = " ".join(
                    content.split()
                )

                if len(content) > 250:

                    content = (
                        content[:250]
                        + "..."
                    )

                all_results.append(
                    {
                        "title": title,
                        "url": url,
                        "content": content,
                    }
                )

        # -------------------------------------------------
        # Remove duplicate URLs
        # -------------------------------------------------

        unique_results = []

        seen_urls = set()

        for result in all_results:

            url = result.get(
                "url",
                ""
            ).strip()

            if not url:
                continue

            normalized_url = url.rstrip(
                "/"
            ).lower()

            if normalized_url in seen_urls:
                continue

            seen_urls.add(
                normalized_url
            )

            unique_results.append(
                result
            )

        # -------------------------------------------------
        # Remove obvious non-job pages
        # -------------------------------------------------

        filtered_results = []

        blocked_words = [
            "blog",
            "article",
            "news",
            "tutorial",
            "course",
            "salary",
            "guide",
            "resources",
            "documentation",
            "docs",
        ]

        for result in unique_results:

            title = result.get(
                "title",
                ""
            ).lower()

            url = result.get(
                "url",
                ""
            ).lower()

            combined = (
                title
                + " "
                + url
            )

            blocked = any(
                word in combined
                for word in blocked_words
            )

            if blocked:
                continue

            filtered_results.append(
                result
            )

        # -------------------------------------------------
        # Keep maximum 15 candidates
        # -------------------------------------------------

        filtered_results = (
            filtered_results[:15]
        )

        # -------------------------------------------------
        # Build concise output
        # -------------------------------------------------

        output_lines = []

        for index, result in enumerate(
            filtered_results,
            start=1,
        ):

            title = result.get(
                "title",
                "Unknown Job"
            )

            url = result.get(
                "url",
                ""
            )

            snippet = result.get(
                "content",
                ""
            )

            output_lines.append(
                f"{index}. {title}\n"
                f"URL: {url}\n"
                f"Snippet: {snippet}"
            )

        final_content = "\n\n".join(
            output_lines
        )

        if not final_content:

            final_content = (
                "No relevant job postings "
                "were found."
            )

        print(
            f"  ✓ Raw results: "
            f"{len(all_results)}"
        )

        print(
            f"  ✓ Unique results: "
            f"{len(unique_results)}"
        )

        print(
            f"  ✓ Job candidates: "
            f"{len(filtered_results)}"
        )

        return {
            "messages": [
                AIMessage(
                    content=final_content
                )
            ]
        }

    # =====================================================
    # QUERY EXTRACTION
    # =====================================================

    @staticmethod
    def _extract_queries(
        text: str,
    ) -> list[str]:

        queries = []

        if not text:
            return queries

        marker = "Search queries:"

        if marker not in text:

            return queries

        section = text.split(
            marker,
            1
        )[1]

        # Stop before other instructions
        stop_markers = [
            "\n\nUse Tavily",
            "\n\nReturn ONLY",
            "\n\nPrefer",
            "\n\nExclude",
        ]

        for marker_text in stop_markers:

            if marker_text in section:

                section = section.split(
                    marker_text,
                    1
                )[0]

                break

        for line in section.splitlines():

            line = line.strip()

            if not line:
                continue

            line = line.lstrip(
                "-•0123456789. "
            ).strip()

            if not line:
                continue

            queries.append(
                line
            )

        # Remove duplicates
        unique_queries = []

        for query in queries:

            query_lower = query.lower()

            if query_lower in [
                q.lower()
                for q in unique_queries
            ]:
                continue

            unique_queries.append(
                query
            )

        return unique_queries[:4]


# =========================================================
# EXPORT
# =========================================================

job_search_agent = JobSearchAgent()