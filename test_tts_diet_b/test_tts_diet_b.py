import os
import inspect
import tts_diet_b
import unittest
import math
from collections import defaultdict
from ticdat import Slicer

def _this_directory() :
    return os.path.dirname(os.path.realpath(os.path.abspath(inspect.getsourcefile(_this_directory))))

def get_test_data(data_set_name):
    path = os.path.join(_this_directory(), "data", data_set_name)
    assert os.path.exists(path), f"bad path {path}"
    # right now assumes data is archived as a single json file for each data set
    if os.path.isfile(path):
        return tts_diet_b.input_schema.json.create_pan_dat(path)

def _smaller(x, y, epsilon=1e-5):
    return x < y and not math.isclose(x, y, rel_tol=epsilon)


class TestDiet(unittest.TestCase):

    def _sln_validate(self, dat, sln): # the solution validator
        dat = tts_diet_b.input_schema.copy_to_tic_dat(dat)
        sln = tts_diet_b.solution_schema.copy_to_tic_dat(sln)
        cn = defaultdict(float)
        nq = Slicer(dat.nutrition_quantities)
        for k, v in sln.buy_food.items():
            for f, c in nq.slice(k, '*'):
                cn[c] += dat.nutrition_quantities[f, c]["Quantity"] * v["Quantity"]
        cn = {k: v for k, v in cn.items() if v > 0}
        self.assertTrue(set(cn) == {k for k, v in sln.consume_nutrition.items() if v["Quantity"] > 0})
        self.assertTrue(all(math.isclose(v, sln.consume_nutrition[k]["Quantity"], rel_tol=1e-5) for k, v in cn.items()))
        for k, v in dat.categories.items():
            self.assertTrue((1 - 1e-5) * v["Min Nutrition"] <= cn.get(k, 0) <= (1 + 1e-5) * v["Max Nutrition"])
        self.assertTrue(math.isclose(sum(dat.foods[k]["Cost"] * v["Quantity"] for k, v in sln.buy_food.items()),
                        sln.parameters["Total Cost"]["Value"], rel_tol=1e-5))

    # This is a pretty simple test suite - just two data sets. But the template should be clear for how you could
    # archive many useful data sets for validating your optimization engine.
    def test_standard_data_set(self):
        dat = get_test_data("standard_data_set.json")
        sln = tts_diet_b.solve(dat)
        self._sln_validate(dat, sln)
        self.assertTrue(math.isclose(sln.parameters.loc[sln.parameters["Parameter"] == "Total Cost", "Value"].iloc[0],
                                     11.82886, rel_tol=1e-5))
        # The test_ subroutine can stop here and still be a good test. The rest of the subroutine
        # demonstrates how you can validate the objective function is being handled by the optimization
        max_idx = sln.buy_food["Quantity"].idxmax()
        most_eaten = sln.buy_food.loc[max_idx, "Food"]
        dat.foods.loc[dat.foods["Name"] == most_eaten, "Cost"] *= 10
        sln2 = tts_diet_b.solve(dat)
        sln_most_eaten = lambda sln_: sln_.buy_food.loc[sln_.buy_food["Food"] == most_eaten, "Quantity"].iloc[0]
        self.assertTrue(_smaller(11.82886,
                                 sln2.parameters.loc[sln2.parameters["Parameter"] == "Total Cost", "Value"].iloc[0]))
        self.assertTrue(most_eaten not in set(sln2.buy_food["Food"]) or
                        _smaller(sln_most_eaten(sln2), sln_most_eaten(sln)))

    def test_neos_guide_data_set(self):
        # Reproducing the result from here https://neos-guide.org/content/diet-problem.
        # Note that they have a constraint on servings per foods, which we model using dummy categories.
        dat = get_test_data("neos_data_set.json")
        sln = tts_diet_b.solve(dat)
        self._sln_validate(dat, sln)
        self.assertTrue(all(math.isclose(sln.buy_food.loc[sln.buy_food["Food"] == f, "Quantity"].iloc[0],
                                         qty, rel_tol=1e-5)
                            for f, qty in [["Corn", 1.94444], ["2% Milk", 10], ["Wheat Bread", 10]]))

# Run the tests via the command line
if __name__ == "__main__":
    unittest.main()
