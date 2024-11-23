"""
Models for Marvel API.
"""

from typing import List


class Character:
    """
    A Marvel character.
    """

    def __init__(self, id: str, name: str, description: str, thumbnail: str):
        self.id = id
        self.name = name
        self.description = description
        self.thumbnail = thumbnail

    @staticmethod
    def from_api_result(result):
        """
        Create a Character from an API result.
        """
        return Character(
            id=str(result.get("id", "")),
            name=result.get("name", ""),
            description=result.get("description", ""),
            thumbnail=f"{result['thumbnail']['path']}.{result['thumbnail']['extension']}",
        )

    @staticmethod
    def list_from_api_results(results: List[dict]):
        """
        Create a list of Characters from a list of API results.
        """
        return [Character.from_api_result(result) for result in results]
