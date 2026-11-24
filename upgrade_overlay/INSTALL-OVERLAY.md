# Apply this upgrade to your GitHub repository

Your uploaded repository currently contains the `multi_agent_practice/` folder only. This overlay keeps that folder as the project and adds `.github/workflows/` at the repository root.

1. Extract this ZIP.
2. Copy/merge the extracted `.github/` folder into the root of your GitHub repository.
3. Replace/merge the repository's existing `multi_agent_practice/` folder with the new `multi_agent_practice/` folder from this ZIP. The prior simulation is retained only as a teaching artifact if you copy its `src/demo.py` manually; the new implementation uses `src/cli.py`.
4. Commit and push.
5. Add API keys as GitHub Actions Secrets and model IDs as repository Variables (see `multi_agent_practice/README.md`).

Do not upload `.env` or API keys. The `.env.example` file is safe to commit.
