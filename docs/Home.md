name: Wiki Content Sync

on:
  push:
    branches:
      - master
      - main
    paths:
      - "docs/**"
  repository_dispatch:
    types: [docs]
  workflow_dispatch:
  gollum:
  
env:
  GIT_AUTHOR_NAME: GitHub Action
  GIT_AUTHOR_EMAIL: action@github.com
  SYNC_CHANGES_REPO_NAME: docs-sync

jobs:

  sync-content-to-wiki:
    if: always() && format('refs/heads/{0}', github.event.repository.default_branch) == github.ref && github.event_name != 'gollum'
    runs-on: [ ubuntu-latest ]
    steps:      
      - uses: actions/checkout@v3
      - name: Sync docs folder to wiki
        uses: newrelic/wiki-sync-action@v1.0.1
        with:
          source: docs
          destination: wiki
          token: ${{ secrets.WIKI_SYNC_SECRET }}
          gitAuthorName: ${{ env.GIT_AUTHOR_NAME }}
          gitAuthorEmail: ${{ env.GIT_AUTHOR_EMAIL }}

  job-sync-wiki-to-docs:
    if: github.event_name == 'gollum'
    runs-on: [ ubuntu-latest ]
    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3
        with:
          token: ${{ secrets.WIKI_SYNC_SECRET }}
          ref: ${{ github.event.repository.default_branch }}
      - name: Is this safe to do?
        id: safe
        run: |
          # to check if the Home.md file exists locally already, is so we can assume a sync has been done, and bidirection can now run safely.
          INDEX_EXISTS=$(find docs/* -name "Home.md")
          
          if [ ! -z $INDEX_EXISTS ] 
          then
            echo "not a first time run"
          else
            OUTPUT="# Oopsy, we've hit a road block, but we're almost there \n
            :rocket: - you are on your way, but first you need to sync content to the wiki first before the reverse can happen else you will lose data\n
            this can be done by running this job manually on your default branch whilst ensuring you have\n
            created a md file in docs named Home.md to pass this step"
            echo -e $OUTPUT >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
        shell: bash
      - name: Create branch first
        run: |
          git checkout -b $SYNC_CHANGES_REPO_NAME
        shell: bash
      - name: Sync Wiki to Docs
        uses: newrelic/wiki-sync-action@v1.0.1
        with:
          source: wiki
          destination: docs
          token: ${{ secrets.WIKI_SYNC_SECRET }}
          gitAuthorName: ${{ env.GIT_AUTHOR_NAME }}
          gitAuthorEmail: ${{ env.GIT_AUTHOR_EMAIL }}
          branch: ${{ env.SYNC_CHANGES_REPO_NAME }}
          
      - name: Create pull-request
        uses: repo-sync/pull-request@v2
        with:
          source_branch: ${{ env.SYNC_CHANGES_REPO_NAME }}
          destination_branch: ${{ github.event.repository.default_branch }}
          pr_title: "[Chore] - Syncing Wiki changes in ${{ env.SYNC_CHANGES_REPO_NAME }} into default branch"
          pr_body: ":crown: *An automated PR* This is an automated PR to sync this repository's wiki docs with your docs in the repo via a PR."
          pr_label: "docs,automation"
          pr_draft: false
          pr_allow_empty: false
          github_token: ${{ secrets.WIKI_SYNC_SECRET }}