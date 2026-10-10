import argparse
import asyncio
import json
import sys
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.config import BACKEND, Settings
from app.database import make_engine
from app.dataset import Catalog, geojson, load_dataset, validate_dataset
from app.generator import GenerationOptions, generate
from app.seeding import seed_database


def write_json(path: Path, value: dict, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise ValueError(f"Output already exists: {path}; use --overwrite explicitly")
    path.parent.mkdir(parents=True, exist_ok=True)
    # Build/validate first, then atomically replace the output. Failed generation writes nothing.
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


async def seed(settings, dataset, catalog, replace):
    engine = make_engine(settings.database_url)
    try:
        await seed_database(engine, dataset, catalog, replace=replace)
    finally:
        await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="StayScape offline M2 dataset tools")
    commands = parser.add_subparsers(dest="command", required=True)
    generation = commands.add_parser("generate")
    generation.add_argument("--count", type=int, default=300)
    generation.add_argument("--seed", type=int, default=42)
    generation.add_argument("--min-spacing-m", type=float)
    generation.add_argument("--attempts-per-region", type=int, default=30_000)
    generation.add_argument("--out", type=Path, default=BACKEND / "data/listings.json")
    generation.add_argument("--overwrite", action="store_true")
    for name in ("validate", "seed", "export-geojson"):
        command = commands.add_parser(name)
        command.add_argument("--input", type=Path, default=BACKEND / "data/listings.json")
        if name == "seed":
            command.add_argument("--replace", action="store_true")
        if name == "export-geojson":
            command.add_argument("--out", type=Path, default=BACKEND / "data/listings.geojson")
            command.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        settings = Settings()
        catalog = Catalog(settings)
        if args.command == "generate":
            dataset = generate(
                catalog,
                GenerationOptions(
                    count=args.count,
                    seed=args.seed,
                    min_spacing_m=args.min_spacing_m,
                    attempts_per_region=args.attempts_per_region,
                ),
            )
            write_json(args.out, dataset.model_dump(mode="json"), overwrite=args.overwrite)
            print(json.dumps(validate_dataset(dataset, catalog), indent=2))
        else:
            dataset = load_dataset(args.input, catalog)
            if args.command == "validate":
                print(json.dumps(validate_dataset(dataset, catalog), indent=2))
            elif args.command == "seed":
                asyncio.run(seed(settings, dataset, catalog, args.replace))
                print(f"Seeded {dataset.count} synthetic {dataset.currency} listings.")
            else:
                write_json(args.out, geojson(dataset, catalog.geography), overwrite=args.overwrite)
                print(f"Exported {dataset.count} points, regions and exclusions to {args.out}")
        return 0
    except ValidationError as exc:
        print(
            f"VALIDATION_ERROR: {exc.error_count()} invalid field(s); check input/configuration.",
            file=sys.stderr,
        )
    except SQLAlchemyError:
        print(
            "DATABASE_ERROR: seed failed; check the configured database and schema.",
            file=sys.stderr,
        )
    except (ValueError, OSError) as exc:
        print(f"DATASET_ERROR: {exc}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
