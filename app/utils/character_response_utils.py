"""
Utility functions for building gRPC CharacterResponse objects.
"""

import logging

from app.grpc_services.proto import marvel_pb2

logger = logging.getLogger(__name__)


def build_character_response(api_response):
    """
    Convert the Marvel API response into a gRPC response format.
    :param api_response: JSON response from the Marvel API or cache.
    :return: gRPC CharacterResponse
    """
    characters = [
        marvel_pb2.Character(
            id=result.get("id", 0),
            name=result.get("name", ""),
            description=result.get("description", ""),
            thumbnail=(
                marvel_pb2.Image(
                    path=result["thumbnail"]["path"],
                    extension=result["thumbnail"]["extension"],
                )
                if result.get("thumbnail")
                else None
            ),
            comics=build_resource_list(result.get("comics", {}), "comics"),
            stories=build_resource_list(result.get("stories", {}), "stories"),
            events=build_resource_list(result.get("events", {}), "events"),
            series=build_resource_list(result.get("series", {}), "series"),
        )
        for result in api_response.get("data", {}).get("results", [])
    ]

    return marvel_pb2.CharacterResponse(
        code=api_response.get("code", 0),
        status=api_response.get("status", ""),
        copyright=api_response.get("copyright", ""),
        attributionText=api_response.get("attributionText", ""),
        attributionHTML=api_response.get("attributionHTML", ""),
        etag=api_response.get("etag", ""),
        offset=api_response.get("data", {}).get("offset", 0),
        limit=api_response.get("data", {}).get("limit", 0),
        total=api_response.get("data", {}).get("total", 0),
        count=api_response.get("data", {}).get("count", 0),
        characters=characters,
    )


def build_resource_list(resource_data, resource_type):
    """
    Build a ResourceList from the given resource data.
    :param resource_data: The resource data dictionary.
    :param resource_type: The type of resource (comics, stories, etc.).
    :return: gRPC ResourceList
    """
    try:
        if not resource_data or resource_type not in {
            "comics",
            "stories",
            "events",
            "series",
        }:
            return marvel_pb2.ResourceList()

        summary_class = {
            "comics": marvel_pb2.ComicSummary,
            "stories": marvel_pb2.StorySummary,
            "events": marvel_pb2.EventSummary,
            "series": marvel_pb2.SeriesSummary,
        }

        summaries = []
        for item in resource_data.get("items", []):
            summary_kwargs = {
                "resourceURI": item.get("resourceURI", ""),
                "name": item.get("name", ""),
            }

            # Only add "type" field for stories
            if resource_type == "stories":
                summary_kwargs["type"] = item.get("type", "")

            summaries.append(summary_class[resource_type](**summary_kwargs))

        return marvel_pb2.ResourceList(
            available=resource_data.get("available", 0),
            returned=len(summaries),
            collectionURI=resource_data.get("collectionURI", ""),
            **{resource_type: summaries},
        )
    except Exception as e:
        logger.error(
            "[build_resource_list] Error building ResourceList for %s: %s",
            resource_type,
            e,
        )
        return marvel_pb2.ResourceList()
