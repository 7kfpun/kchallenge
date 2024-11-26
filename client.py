"""
Marvel gRPC client.
"""

# pylint: disable=no-member
import grpc
import app.grpc_services.proto.marvel_pb2 as marvel_pb2
import app.grpc_services.proto.marvel_pb2_grpc as marvel_pb2_grpc


def fetch_characters(name_starts_with: str, offset: int, limit: int):
    """Fetch Marvel characters using the gRPC client."""
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = marvel_pb2_grpc.MarvelServiceStub(channel)
        request = marvel_pb2.CharacterRequest(
            name_starts_with=name_starts_with, offset=offset, limit=limit
        )
        return stub.GetCharacters(request)


def display_response(response: marvel_pb2.CharacterResponse):
    """Display the response from the server."""
    print(f"Code: {response.code}")
    print(f"Status: {response.status}")
    print(f"Copyright: {response.copyright}")
    print(f"AttributionText: {response.attributionText}")
    print(f"AttributionHTML: {response.attributionHTML}")
    print(f"Etag: {response.etag}")
    print(f"Offset: {response.offset}")
    print(f"Limit: {response.limit}")
    print(f"Total: {response.total}")
    print(f"Count: {response.count}")
    print("\nCharacters:")
    for character in response.characters:
        print(f"- ID: {character.id}")
        print(f"  Name: {character.name}")
        print(f"  Description: {character.description}")
        print(
            f"  Thumbnail: {character.thumbnail.path}.{character.thumbnail.extension}"
        )
        print("  Comics:")
        for comic in character.comics.comics:
            print(f"    - {comic.name}")
        print("  Stories:")
        for story in character.stories.stories:
            print(f"    - {story.name} ({story.type})")
        print("  Events:")
        for event in character.events.events:
            print(f"    - {event.name}")
        print("  Series:")
        for series in character.series.series:
            print(f"    - {series.name}")
        print("\n")


if __name__ == "__main__":
    query = input("Enter a character name (or part of it) to search: ")
    offset = int(input("Enter the offset (start at 0): "))
    limit = int(input("Enter the limit (e.g., 5 or 10): "))

    try:
        response = fetch_characters(name_starts_with=query, offset=offset, limit=limit)
        display_response(response)
    except grpc.RpcError as e:
        print(f"Error: {e.code()} - {e.details()}")
