# Contribution guidelines for sagemaker-code-gen

## Testing
* To check for regressions in existing flows, make sure to run: `pytest tst`. For new unit test coverage added make sure `pytest tst` validates them. 

```angular2html
# assuming operating within `sagemaker-code-gen` workspace 
export PYTHONPATH=${PYTHONPATH}:#{pwd}
pytest tst
```