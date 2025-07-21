#!/bin/sh

set -o errexit

if [ ! -d questions.yaml.d ]; then
	echo "no questions.yaml.d found in current directory exiting!" >&2
	exit 1
fi

cp questions.yaml.d/header.yaml questions.yaml

for hopp in questions.yaml.d/hoppscotch/*.yaml; do
	tail -n +8 "$hopp" >>questions.yaml
done

cat questions.yaml.d/oauth-header.yaml >>questions.yaml
for hopp in questions.yaml.d/hoppscotch-oauth/*.yaml; do
	tail -n +13 "$hopp" >>questions.yaml
done

for sections in network storage labels resources; do
	echo "" >>questions.yaml
	tail -n +2 questions.yaml.d/$sections.yaml >>questions.yaml
done
