"""
Marvel gRPC client with query-specific streaming updates.
"""

import grpc
from app.grpc_services.proto import marvel_pb2, marvel_pb2_grpc


def fetch_characters(name_starts_with: str, offset: int, limit: int):
    """
    Fetch Marvel characters using the gRPC client.
    """
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = marvel_pb2_grpc.MarvelServiceStub(channel)
        request = marvel_pb2.CharacterRequest(
            name_starts_with=name_starts_with, offset=offset, limit=limit
        )
        response = stub.GetCharacters(request)
        display_response(response)


def stream_updates(name_starts_with: str, offset: int, limit: int):
    """
    Subscribe to Marvel character updates for a specific query using gRPC streaming.
    """
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = marvel_pb2_grpc.MarvelServiceStub(channel)
        request = marvel_pb2.CharacterRequest(
            name_starts_with=name_starts_with, offset=offset, limit=limit
        )
        try:
            for response in stub.StreamUpdates(request):
                print("Received an update for your query:")
                display_response(response)
        except grpc.RpcError as e:
            print(f"Streaming error: {e.code()} - {e.details()}")


def display_response(response: marvel_pb2.CharacterResponse):
    """
    Display the response from the server.
    """
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
    print("Choose an option:")
    print("1. Fetch Characters")
    print("2. Subscribe to Updates")

    choice = input("Enter your choice: ")

    if choice == "1":
        query = input("Enter a character name (or part of it) to search: ")
        offset = int(input("Enter the offset (start at 0): "))
        limit = int(input("Enter the limit (e.g., 5 or 10): "))
        fetch_characters(query, offset, limit)
    elif choice == "2":
        query = input("Enter a character name (or part of it) to stream updates: ")
        offset = int(input("Enter the offset (start at 0): "))
        limit = int(input("Enter the limit (e.g., 5 or 10): "))
        print("Subscribing to updates for your query...")
        stream_updates(query, offset, limit)
    else:
        print("Invalid choice.")
