.PHONY: sync lint fmt test validate check new-plugin

sync:
	uv sync --all-packages --locked

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

test:
	uv run pytest

validate:
	claude plugin validate .

check: lint test validate

new-plugin:
	@test -n "$(NAME)" || (echo "usage: make new-plugin NAME=<slug> [DESC=\"...\"]"; exit 1)
	./scripts/new_plugin.sh $(NAME) "$(DESC)"
