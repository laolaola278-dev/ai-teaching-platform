# AI Teaching Platform - Agent Instructions

## Repository Structure

This repository contains educational reference implementations for AI/ML teaching:

- `references/fastbook/` - Jupyter notebooks from the fast.ai book (educational content)
- `references/llm-from-scratch/` - From-scratch LLM implementation in PyTorch (educational codebase)

## Key Commands

### llm-from-scratch Project
- **Test**: `uv run pytest` (from `references/llm-from-scratch/`)
- **Training**: `uv run -m llm.training`
- **Distributed training**: `uv run -m llm.training --world_size 6 --batch_size 768`
- **Text generation**: `uv run -m llm.generating`
- **Tokenizer training**: `uv run -m llm.bpe_tokenizer`
- **SFT evaluation**: `uv run -m alignment.evaluate`
- **SFT fine-tuning**: `uv run -m alignment.sft`
- **RL fine-tuning**: `uv run -m alignment.train_rl`

### fastbook Project
- **Environment**: Uses `requirements.txt` for dependencies
- **Content**: Educational Jupyter notebooks (read-only reference material)

## Toolchain Notes

### llm-from-scratch
- Uses `uv` package manager (not pip/conda)
- Python 3.11-3.12 required (see `pyproject.toml`)
- Ruff configured with 120 line length
- Tests use pytest with `-s` flag (no output capture)
- Flash Attention 2 implemented via Triton
- Distributed training via custom DDP implementation

### fastbook
- Standard pip/conda environment
- Jupyter notebooks for interactive learning
- Copyright restrictions apply (see README)

## Development Guidelines

1. **llm-from-scratch is the primary development area** - This contains actual code to modify
2. **fastbook is reference material** - Notebooks are educational content, not for modification
3. **Use uv for llm-from-scratch** - Commands must be prefixed with `uv run`
4. **Test before changes** - Run `uv run pytest` to ensure tests pass
5. **Follow existing patterns** - Code uses modern PyTorch patterns with custom implementations

## Testing & Quality

- **Linting**: Ruff with 120 char line length
- **Type checking**: Jaxtyping for tensor type hints
- **Test coverage**: Comprehensive pytest suite covering all modules
- **Benchmarks**: Separate benchmark scripts in `bench_mark/` directory

## Important Constraints

- **Copyright**: fastbook materials have strict copyright (no redistribution/modification)
- **Educational focus**: Code is designed for clarity over optimization
- **Modularity**: Components are intentionally separated for educational value
- **Documentation**: README files contain detailed usage instructions