"""Runtime compatibility contract for the approved MMold Hub baseline."""

from mmold_hub import __version__ as MMOLD_HUB_VERSION

EXPECTED_FRAPPE_VERSION = "16.36.0"
EXPECTED_ERPNEXT_VERSION = "16.37.0"
MMOLD_HUB_MAJOR_OFFSET = 10


class IncompatibleRuntimeError(RuntimeError):
	"""Raised when the installed runtime is outside the approved baseline."""


def normalize_version(value: object) -> str:
	"""Normalize a release string without accepting a different version."""
	return str(value or "unknown").strip().removeprefix("v")


def validate_versions(
	frappe_version: object,
	erpnext_version: object,
	mmold_hub_version: object | None = None,
) -> None:
	actual_frappe = normalize_version(frappe_version)
	actual_erpnext = normalize_version(erpnext_version)
	actual_mmold_hub = normalize_version(mmold_hub_version or MMOLD_HUB_VERSION)
	expected_mmold_hub = _expected_mmold_hub_version(actual_erpnext)
	if (
		actual_frappe != EXPECTED_FRAPPE_VERSION
		or actual_erpnext != EXPECTED_ERPNEXT_VERSION
		or actual_mmold_hub != expected_mmold_hub
	):
		raise IncompatibleRuntimeError(
			f"MMold Hub {expected_mmold_hub} requires "
			f"Frappe {EXPECTED_FRAPPE_VERSION} and ERPNext {EXPECTED_ERPNEXT_VERSION}; "
			f"detected MMold Hub {actual_mmold_hub}, Frappe {actual_frappe} "
			f"and ERPNext {actual_erpnext}."
		)


def _expected_mmold_hub_version(erpnext_version: str) -> str:
	parts = erpnext_version.split(".")
	if len(parts) != 3 or not all(part.isdigit() for part in parts):
		return "unknown"
	major, minor, patch = (int(part) for part in parts)
	if major < MMOLD_HUB_MAJOR_OFFSET:
		return "unknown"
	return f"{major - MMOLD_HUB_MAJOR_OFFSET}.{minor}.{patch}"


def validate_runtime() -> None:
	"""Validate versions inside a Frappe Bench process."""
	import erpnext
	import frappe

	validate_versions(
		getattr(frappe, "__version__", "unknown"),
		getattr(erpnext, "__version__", "unknown"),
		MMOLD_HUB_VERSION,
	)
