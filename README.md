# Dashboard for Awesome-*

This project contains Python scripts for data parsing, aggregating, and generating dashboards for awesome-*.

Files:
  - config.yml: configuration file for awesome repo urls, GitHub credentials, and Database credentials
  - smart_downloading_data.py: downloading GitHub event data from githubarchive.org
  - get_all_getub_repos.py: extract all GitHub repositories from an awesome-* project
  - create_all_activities.py: parse githubarchive event data, and extract all event data of a set of GitHub repositories that are indexed by a specific awesome-* repo
  - get_repo_info.py: get the info of GitHub repositories that are indexed by a specific awesome-* repo
  - build_dashboard.py: build a Dashboard all all the repo info with GitHub Flavored Markdown

Let me know if you have any questions of suggestions. Thanks!
