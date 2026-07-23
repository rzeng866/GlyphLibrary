"""Presentation layer: text summaries, charts, and PDF reports."""

from .pdf import render_pdf
from .text import render_summary

__all__ = ["render_pdf", "render_summary"]
