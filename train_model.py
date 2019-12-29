from tools import *
import lightgbm as lgm
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV


X, y = fetch_training()

feature_engineer = FeatureEngineerTransformer()

# Initialize model
gbm_model = lgm.LGBMRegressor(
    n_estimators=1000,
    objective="mean_absolute_error",
    learning_rate=0.01,
    boosting_type="gbdt",
    colsample_bytree=0.55)

# Remember, raw data comes through the Pipeline
# Is transformed by FeatureEngineerTransformer
# And then passed to model

model_pipe = Pipeline(
    [("feature_engineering", feature_engineer),
    ("scaler", MinMaxScaler(feature_range=(-1, 1))),
    ("model", gbm_model)])

params = {
    "model__reg_alpha": [0, 10, 35, 50, 100],
    "model__reg_lambda": [100, 200, 250, 300],
    "model__max_depth": [10, 1000, 2500, None],
    "model__num_leaves": [25, 50, 100, 250, None],
    "model__subsample": [0.1, 0.2, 0.5, 0.8, 1],
    "model__min_data_in_leaf": [20, 250, 500, 1000]
    }


training_ix, cv_set, testing_ix = make_validation_ix(X)

gscv = GridSearchCV(
    model_pipe,
    param_grid=params,
    return_train_score=True,
    verbose=1,
    cv=cv_set,
    scoring="neg_mean_absolute_error",
    n_jobs=-1,
    iid=False,
    refit=True,
)

# The cv set still works even though I am slicing out the current year
gscv.fit(X.iloc[training_ix,], y[training_ix])
test_preds = gscv.predict(X.iloc[testing_ix,])

print("############################")
print("Best params: ", gscv.best_params_)
print("Best model score: ", np.round(gscv.best_score_, 2))
print("#############################")

# Save model
with open("model.txt", "wb") as model_file:
    pickle.dump(gscv, model_file)
