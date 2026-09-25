"""Convert WGS 84 geographic coordinates to WGS 84 geocentric coordinates.

Input rows must contain: name, type, latitude, longitude, height.
The output contains: name, type, X, Y, Z, where X/Y/Z are in metres.
"""

import argparse
import csv
from pathlib import Path

from pyproj import Transformer


# EPSG:4326 is WGS 84 geographic coordinates (longitude, latitude, height)
# EPSG:4978 is WGS 84 geocentric coordinates (X, Y, Z)
TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:4978", always_xy=True)


def convert_file(input_path, output_path):
	"""Convert all coordinate rows from *input_path* into *output_path*."""
	with input_path.open("r", newline="", encoding="utf-8") as source:
		reader = csv.reader(source)
		with output_path.open("w", newline="", encoding="utf-8") as target:
			writer = csv.writer(target)
			for line_number, row in enumerate(reader, start=1):
				if not row or not any(field.strip() for field in row):
					continue
				if row[0].lstrip().startswith("#"):
					continue
				if len(row) != 5:
					raise ValueError(
						f"line {line_number}: expected 5 comma-separated fields"
					)

				name, point_type, latitude, longitude, height = row
				try:
					x, y, z = TRANSFORMER.transform(
						float(longitude), float(latitude), float(height)
					)
				except ValueError as error:
					raise ValueError(
						f"line {line_number}: invalid coordinate value"
					) from error
				writer.writerow([name.strip(), point_type.strip(), x, y, z])


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("input", type=Path, help="input TXT/CSV file")
	parser.add_argument(
		"output",
		type=Path,
		nargs="?",
		help="output TXT/CSV file (default: <input>_ecef<suffix>)",
	)
	args = parser.parse_args()
	output_path = args.output or args.input.with_name(
		f"{args.input.stem}_ecef{args.input.suffix}"
	)
	convert_file(args.input, output_path)
	print(f"Saved {output_path}")


if __name__ == "__main__":
	main()
