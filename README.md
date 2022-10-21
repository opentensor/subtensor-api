# subtensor-api

## Release subtensor-api python package

In order to release the subtensor-api python package we should:

1. Update version (update_version.sh)
1. Release package (release.sh)
    1. Tag github repo
    1. Generate github release
    1. Update python wheel to pypi

You can do this with the following commands:

```
cd subtensor-api/ && \
./scripts/release/update_version.sh minor && \
./scripts/release/release.sh
```

> Note that this command will release a minor version. For major or patch version change the usage of the update_version.sh script (major, minor and patch are allowed). 