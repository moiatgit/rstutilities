echo "This script downloads the language icon defined in args and stores it in cwd"

base_url=https://cdn.jsdelivr.net/npm/devicon@latest/icons
for i in "$@"; do
    echo "Downloading $i"
    wget $base_url/$i/$i-original.svg
done
