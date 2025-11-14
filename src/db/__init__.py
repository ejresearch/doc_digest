"""
GRAFF Database Module

Provides database connection and persistence functions for GRAFF chapter analysis.
"""

from .connection import (
    get_connection,
    init_database,
    save_chapter_analysis,
    load_chapter_analysis,
    list_chapters,
    delete_chapter,
    backup_database,
    repair_database_triggers
)

__all__ = [
    'get_connection',
    'init_database',
    'save_chapter_analysis',
    'load_chapter_analysis',
    'list_chapters',
    'delete_chapter',
    'backup_database',
    'repair_database_triggers'
]
