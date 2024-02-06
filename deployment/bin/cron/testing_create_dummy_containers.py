import docker

# Create a container with ee2 labels and username labels
# Fake the creation time to be 7 days ago

client = docker.from_env()
c = client.containers.run("ubuntu:latest", "/bin/sleep infinity", labels={"user_name": "test_user", "ee2_endpoint":
    "https://ci.kbase.us/services/ee2"},
                      detach=True,
                      name="test_container2",
                      auto_remove=True)

def remove_with_backoff(container,message,backoff=30):
    try:
        container.stop()
        import time
        time.sleep(backoff)  # Wait for backoff period before attempting to remove
        container.remove()
    except Exception as e:
        pass

remove_with_backoff(c,"test_container2")
