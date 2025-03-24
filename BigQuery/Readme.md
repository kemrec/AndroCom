In the Google BigQuery console, we will process the following commands in that console. 

#1. Find repositories that contain "AndroidManifest.xml" files.
```SELECT
      repo_name,
      path,
      id
    FROM
      bigquery-public-data.github_repos.files
    WHERE
      path LIKE
        '%AndroidManifest.xml'
```

#2. Obtain the contents of the files that we are interested in.
```
    SELECT
      M.id as id,
      M.repo_name as repo_name,
      M.path as path,
      C.content as content
    FROM
      `<table_of_manifest_files>` AS M
    JOIN
      bigquery-public-data.github_repos.contents AS C
    ON
      M.id = C.id
    WHERE
      NOT C.binary

```
#3. Filter the commits that contain specific keywords in their message field.
```
WITH flat_commits AS (
  SELECT 
    repo_name_element AS repo_name,
    b.message AS message,
    b.commit AS commit
  FROM 
    bigquery-public-data.github_repos.commits AS b,
    UNNEST(b.repo_name) AS repo_name_element
  JOIN (
    SELECT a.repo_name
    FROM <contents_of_the_manifest_files> AS a
  ) AS a
  ON repo_name_element = a.repo_name
  WHERE 
    b.message IS NOT NULL 
    AND b.message != ''
    AND REGEXP_CONTAINS(b.message, r'(?i)(denial.of.service|\bXXE\b|remote.code.execution|\bopen.redirect|OSVDB|\bvuln|\bCVE\b|\bCWE\b|\bXSS\b|\bReDoS\b|\bNVD\b|x−frame−options|vulner[a-z]+|cross.site|exploit|malicious|directory.traversal|\bRCE\b|\bdos\b|\bDoS\b|\bXSRF\b|\bCSRF\b|\bXSS\b|clickjack|session.fixation|hijack|\badvisory|\binsecure|\bcross−origin\b|unauthori[z|s]ed|infinite.loop|authenticat(?:e|ed|ion)|\b(in)?secur(e|ity)|race.condition|dead.code|deadlock|infinite.loop|uncaught.exception|divide.by.zero|null.pointer.dereference|double.free|buffer.overflow|sql.injection|off-by-one.error|encoding.error|\bcsrf\b|incorrect.synchronization|incorrect.calculation|trapdoor|deserialization.of.untrusted.data|leftover.debug.code|missing.handler)')
)

SELECT DISTINCT
  repo_name, 
  message, 
  commit
FROM 
  flat_commits;
```
