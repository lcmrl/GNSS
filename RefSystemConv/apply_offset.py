# Usato nel paper
#  python .\apply_offset.py .\input.txt -0.02 0 -0.02 -o ./aaa.txt --rotation-convention local_to_world --quat-order xyzw

"""Apply a local-frame XYZ offset to pose text files.

Input lines must contain:
	label x y z qx qy qz qw

The offset is interpreted in the local reference system of each pose. The
quaternion is assumed to rotate vectors from the local frame to the global
frame using the active convention.
"""

from __future__ import annotations

import argparse
import math
import os
from typing import List, Sequence, Tuple


Pose = Tuple[str, float, float, float, float, float, float, float]


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Apply a local XYZ offset to each pose in a text file."
	)
	parser.add_argument("input_file", help="Input txt file with label, XYZ and quaternion")
	parser.add_argument(
		"offset_xyz",
		nargs=3,
		type=float,
		metavar="OFFSET",
		help="Offset vector expressed in each pose local frame",
	)
	parser.add_argument(
		"-o",
		"--output-file",
		help="Output txt file. Defaults to <input_name>_offset.txt next to the input file.",
	)
	parser.add_argument(
		"--quat-order",
		choices=("xyzw", "wxyz"),
		default="xyzw",
		help="Quaternion component order in the input file. Default: xyzw",
	)
	parser.add_argument(
		"--rotation-convention",
		choices=("local_to_world", "world_to_local"),
		default="local_to_world",
		help=(
			"How the stored quaternion should be interpreted. "
			"Use world_to_local if your file stores the inverse pose rotation."
		),
	)
	return parser.parse_args()


def parse_pose_line(line: str, quat_order: str) -> Pose | None:
	stripped = line.strip()
	if not stripped or stripped.startswith("#"):
		return None

	parts = stripped.split()
	if len(parts) != 8:
		raise ValueError(
			f"Expected 8 columns per line (label x y z qx qy qz qw), got {len(parts)}: {line.rstrip()}"
		)

	label = parts[0]
	x, y, z = map(float, parts[1:4])
	quat = list(map(float, parts[4:8]))

	if quat_order == "wxyz":
		qw, qx, qy, qz = quat
	else:
		qx, qy, qz, qw = quat

	return label, x, y, z, qx, qy, qz, qw


def normalize_quaternion(qx: float, qy: float, qz: float, qw: float) -> Tuple[float, float, float, float]:
	norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
	if norm == 0.0:
		raise ValueError("Quaternion norm is zero")
	return qx / norm, qy / norm, qz / norm, qw / norm


def rotate_vector_by_quaternion(
	vector: Sequence[float], qx: float, qy: float, qz: float, qw: float
) -> Tuple[float, float, float]:
	vx, vy, vz = vector

	# Quaternion-vector rotation using q * v * q_conjugate.
	uvx = qy * vz - qz * vy
	uvy = qz * vx - qx * vz
	uvz = qx * vy - qy * vx

	uuvx = qy * uvz - qz * uvy
	uuvy = qz * uvx - qx * uvz
	uuvz = qx * uvy - qy * uvx

	two_qw = 2.0 * qw
	return (
		vx + two_qw * uvx + 2.0 * uuvx,
		vy + two_qw * uvy + 2.0 * uuvy,
		vz + two_qw * uvz + 2.0 * uuvz,
	)


def conjugate_quaternion(qx: float, qy: float, qz: float, qw: float) -> Tuple[float, float, float, float]:
	return -qx, -qy, -qz, qw


def apply_local_offset(pose: Pose, offset_xyz: Sequence[float], rotation_convention: str) -> Pose:
	label, x, y, z, qx, qy, qz, qw = pose
	qx, qy, qz, qw = normalize_quaternion(qx, qy, qz, qw)
	if rotation_convention == "world_to_local":
		qx, qy, qz, qw = conjugate_quaternion(qx, qy, qz, qw)
	dx, dy, dz = rotate_vector_by_quaternion(offset_xyz, qx, qy, qz, qw)
	return label, x + dx, y + dy, z + dz, qx, qy, qz, qw


def format_pose(pose: Pose) -> str:
	label, x, y, z, qx, qy, qz, qw = pose
	return f"{label} {x:.10f} {y:.10f} {z:.10f} {qx:.15f} {qy:.15f} {qz:.15f} {qw:.15f}\n"


def main() -> int:
	args = parse_args()
	input_file = args.input_file
	output_file = args.output_file
	if output_file is None:
		base, _ = os.path.splitext(os.path.basename(input_file))
		output_file = os.path.join(os.path.dirname(os.path.abspath(input_file)), f"{base}_offset.txt")

	poses: List[Pose] = []
	with open(input_file, "r", encoding="utf-8") as handle:
		for line in handle:
			pose = parse_pose_line(line, args.quat_order)
			if pose is not None:
				poses.append(pose)

	offset_xyz = tuple(args.offset_xyz)
	transformed_poses = [apply_local_offset(pose, offset_xyz, args.rotation_convention) for pose in poses]

	with open(output_file, "w", encoding="utf-8") as handle:
		for pose in transformed_poses:
			handle.write(format_pose(pose))

	print(f"Processed {len(transformed_poses)} poses")
	print(f"Saved to: {output_file}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
