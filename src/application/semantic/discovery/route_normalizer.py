"""Route Normalizer to unify dynamic HTTP/RPC endpoint paths for matching client calls to servers."""

import re


class RouteNormalizer:
    """Provides path cleaning, dynamic variable collapsing, and route normalization."""

    @staticmethod
    def normalize(route: str) -> str:
        """Transforms route path into a canonical form.

        Examples:
        - "/api/v1/users/{user_id}" -> "api/v1/users/{var}"
        - "http://localhost:8080/users/:id/profile/" -> "users/{var}/profile"
        """
        if not route:
            return ""

        # 1. Remove scheme and host prefix if present (e.g. http://localhost:8080, https://api.service)
        cleaned = re.sub(r"^https?://[^/]+", "", route)

        # 2. Collapse dynamic path variables to a single placeholder: {var}
        # Matches: {id}, :id, <id>, <int:id>, <uuid:user_id>
        # Match braces: {user_id} -> {var}
        cleaned = re.sub(r"\{[a-zA-Z0-9_-]+\}", "{var}", cleaned)
        # Match colons: :user_id -> {var}
        cleaned = re.sub(r"/:[a-zA-Z0-9_-]+", "/{var}", cleaned)
        # Match angle brackets: <int:id> or <id> -> {var}
        cleaned = re.sub(r"<[a-zA-Z0-9_:-]+>", "{var}", cleaned)

        # 3. Clean slashes (strip leading/trailing, collapse duplicate slashes)
        cleaned = cleaned.strip("/")
        cleaned = re.sub(r"/+", "/", cleaned)

        return cleaned.lower()

    @classmethod
    def match_routes(cls, client_route: str, server_route: str) -> bool:
        """Determines if a client-side route invocation matches a server-side route.

        Unifies dynamic parts before matching.
        """
        norm_client = cls.normalize(client_route)
        norm_server = cls.normalize(server_route)

        if not norm_client or not norm_server:
            return False

        # Direct match check
        if norm_client == norm_server:
            return True

        # Check if the client route matches after stripping common API version prefixes if one has it and the other doesn't
        # e.g. client uses "/users/{id}" and server uses "/api/v1/users/{id}"
        prefix_pattern = r"^(api/)?(v\d+/)"
        sub_client = re.sub(prefix_pattern, "", norm_client)
        sub_server = re.sub(prefix_pattern, "", norm_server)

        return sub_client == sub_server
