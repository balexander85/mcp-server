# MCP Server

A Model Context Protocol (MCP) server that provides tools for managing GitHub repositories.

## Overview

This server implements the Model Context Protocol to provide a set of tools for interacting with GitHub repositories. It allows users to list, archive, unarchive, make private, and delete repositories through a standardized interface.

## Features

- List all repositories for the authenticated user
- Filter repositories by archived status
- Filter repositories by fork status
- Delete repositories
- Update repository attributes
- Make repositories private
- Archive and unarchive repositories

## Setup

### Prerequisites

- Python 3.14+
- Docker (for containerized deployment)

### Environment Variables

The server requires a GitHub API token to be set in the environment:

