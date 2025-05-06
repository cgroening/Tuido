# Tuido

Tuido is a simple productivity application that provides a text user interface (TUI) for managing topics, tasks and notes. The fields of the topics can be defined by the user. All data are saved locally – no cloud requirement.

The components are built using the Textual library, offering a modern terminal GUI experience focused on clarity and interactivity.

The purpose of this application is to provide a space for planning and organizing the current day. With its keyboard-driven, minimalist interface, it aims to support an efficient workflow. It is not intended for long-term planning and is meant to complement apps like Notion or OneNote, not replace them.

Use Tuido for everything that is relevant today but can be deleted in the next days. Tuido aims to help you separate temporary stuff from your personal knowledge management.

> [!warning]
> This application is under development. Already implemented features are listed in the following Section. See the roadmap at the end of this file for planned features.

## Current Features

- Minimalistic text user interface – no overhead
- Full keyboard navigation
- Define fields for a topic (e. g. Title, Description, Status, ...)
- Create, edit and delete topics
- Create, edit, move and delete tasks
- Quick notes (displayed as text, as rendered Markdown or both)

## Feature Details

The application is divided into three tabs: Topics, Tasks and Notes.

### Topic management

The Topics Tab provided a user-friendly interface for managing topics. It is composed of to components:

1. Topics Table

   Displays a tabular overview of all topics

2. Form Widgets

   Shows all details of a topic

The structure is dynamically based on configurable fields. The supported field types are:

- XXX
- XXX
- XXX

Example for a config.yaml:

```yaml
XXX
```

### Task management

The Tasks module helps you organize your day by managing current tasks in a Kanban system.

### Notes

The purpose of the Notes module is to provide a place for temporary notes that aren't worth to be organized elsewhere. Changes are automatically saved.

Notes can be displayed as plain text, as rendered Markdown or both on top of each other.

## Roadmap

### Version 0.1

- [x] Basis topic management (CRUD)
- [ ] Basic task management (CRUD)

### Version 0.2

- [ ] Import and export topics as CSV
- [ ] Import and export tasks as CSV
- [ ] Custom sort order for topics
- [ ] Custom sort order for tasks

### After Version 1.0

- [ ] Multilingual support
