# Changelog

## v1.0.3 (2024-09-06)

 * Daily Sync with Botocore v1.35.13 on 2024/09/06 (#180)
 * Add test to check API coverage (#165)
 * Update README.rst (#178)

## v1.0.2 (2024-09-04)

 * Daily Sync with Botocore v1.35.11 on 2024/09/04 (#179)
 * Add serialization for all methods (#177)
 * Add forbid extra for pydantic BaseModel (#173)
 * Add black check (#174)

## v1.0.1 (2024-08-30)

 * fix: SMD pydantic issue (#170)
 * feat: Add get started notebook (#160)
 * update notebooks (#168)
 * fix pyproject.toml (#167)

## v0.1.10 (2024-08-28)


## v0.1.9 (2024-08-28)

 * Update counting method of botocore api coverage (#159)
 * Example notebook for tracking local pytorch experiment (#158)
 * Add gen AI examples (#155)
 * Fix _serialize_args() for dict parameters (#157)

## v0.1.8 (2024-08-21)

 * Daily Sync with Botocore v1.35.2 on 2024/08/21 (#153)

## v0.1.7 (2024-08-13)

 * Daily Sync with Botocore v1.34.159 on 2024/08/13 (#150)
 * feat: add param validation with pydantic validate_call (#149)
 * Update create-release.yml
 * Support textual rich logging for wait methods (#146)
 * Refactor Package structure (#144)
 * Separate environment variable for Sagemaker Core (#147)
 * Add styling for textual rich logging (#145)
 * Replace all Sagemaker V2 Calls (#142)
 * Daily Sync with Botocore v1.34.153 on 2024/08/05 (#143)
 * Update auto-approve.yml
 * Use textual rich logging handler for all loggers (#138)
 * Update auto-approve.yml
 * Add user agent to Sagemaker Core (#140)
 * Switch to sagemaker-bot account (#137)
 * Metrics for boto API coverage (#136)
 * Fix volume_size_in_g_b attribute in example notebooks (#130)

## v0.1.6 (2024-07-25)

 * Add private preview feedback for denesting simplifications (#128)
 * Put Metrics only for Daily Sync API (#125)

## v0.1.5 (2024-07-22)

 * Daily Sync with Botocore v1.34.145 on 2024/07/22 (#127)

## v0.1.4 (2024-07-22)

 * Cleanup Resources created by Integration tests (#120)
 * Enable Botocore sync workflow (#92)

## v0.1.3 (2024-07-18)

 * Daily Sync with Botocore v1.34.143 on 2024/07/11 (#91)
 * Update license classifier (#119)
 * Metrics (#118)
 * Support wait_for_delete method (#114)

## v0.1.2 (2024-07-08)

 * Add additional methods to the unit test framework (#83)
 * Integration tests (#82)
 * Add exception and return type docstring for additional methods (#58)
 * Support SagemakerServicecatalogPortfolio resource (#49)
 * Support last few additional methods (#52)
 * Integration tests (#53)
 * Fix Intelligent defaults decorator conversion (#51)
 * Fix for Issues that came up in integration tests (#50)
 * Resource Unit test Framework and tests (#46)
 * Support resources by create method and move methods under EdgeDeploymentStage to EdgeDeploymentPlan (#48)
 * Support resources that have the List operation but do not have the Describe operation (#45)
 * Fix class method (#44)
 * Update docstring for additional methods (#43)
 * Add Python 3.11 and 3.12 to PR checks (#42)
 * change: update s3 bucket in notebooks and add cell to delete resources (#41)
 * Fix pascal_to_snake for consecutive capitalized characters (#38)
 * Intelligent Defaults with Snake cased arguments (#40)

## v0.1.1 (2024-06-14)

 * Rollback CHANGELOG.md
 * Rollback VERSION
 * prepare release v0.1.2
 * prepare release v0.1.1
 * Add resource class docstring (#37)
 * Create CHANGELOG.md (#39)

## v0.1.0 (2024-06-14)

 * Initial release of SageMaker Core
