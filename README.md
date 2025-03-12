### Pandas based diet example rendered in Tidy, Tested, Safe format

Usage:

```
    python -m tts_diet_b -i input.xlsx -o solution.xlsx
```

Please read [this](https://github.com/ticdat/tts_diet/blob/master/README.md)
to orient yourself. This example is similar, with the following modifications. 

* Demonstrates the modern pyproject.toml method of deploying packages.
* Demonstrates how `PanDatFactory` can be used to present a `pandas.DataFrame` interface to client 
programmers while still allowing for an internal dictionary based representation of tables. 
  * Note that `pandas.DataFrame` objects can be passed directly to the `TicDatFactory.TicDat` 
  constructor, as demonstrated 
  [here](https://github.com/ticdat/ticdat/blob/master/examples/gurobipy/netflow/netflow_other_data_sources.ipynb).
  Using `PanDatFactory` as the exposed schema and dict-of-dicts internally, as this code demonstrates, 
  is just a bit more friendly to client programmers that prefer `pandas`.

### Contents
* `tts_diet_b` The subdirectory that defines the `tts_diet_b` package.
* `test_tts_diet_b` The subdirectory that contains data and code required for testing `tts_diet_b`.
* `pyproject.toml` Standard file for distributing `tts_diet_b`. 

