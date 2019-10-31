import os
import sys
import pandas as pd
from lightwood import Predictor
import lightwood


####################
config = {'input_features': [
                    {'name': 'number_of_bathrooms', 'type': 'numeric'}, {'name': 'sqft', 'type': 'numeric'},
                    {'name': 'location', 'type': 'categorical'}, {'name': 'days_on_market', 'type': 'numeric'},
                    {'name': 'neighborhood', 'type': 'categorical','dropout':0.4},{'name': 'rental_price', 'type': 'numeric'}],
 'output_features': [{'name': 'number_of_rooms', 'type': 'categorical',
                  # 'weights':{
                  #       '0': 0.8,
                  #       '1': 0.6,
                  #       '2': 0.5,
                  #       '3': 0.7,
                  #       '4': 1,
                  # }
}],
 'mixer':{'class': lightwood.BUILTIN_MIXERS.NnMixer}}


# AX doesn't seem to work on the travis version of windows, so don't test it there as of now
if sys.platform not in ['win32','cygwin','windows']:
    config['optimizer'] = lightwood.model_building.BasicAxOptimizer

lightwood.config.config.CONFIG.USE_CUDA = False

df=pd.read_csv("https://mindsdb-example-data.s3.eu-west-2.amazonaws.com/home_rentals.csv")

predictor = Predictor(config)

def iter_function(epoch, error, test_error, test_error_gradient, test_accuracy):
    print(
        'epoch: {iter}, error: {error}, test_error: {test_error}, test_error_gradient: {test_error_gradient}, test_accuracy: {test_accuracy}'.format(
            iter=epoch, error=error, test_error=test_error, test_error_gradient=test_error_gradient,
            accuracy=predictor.train_accuracy, test_accuracy=test_accuracy))


predictor.learn(from_data=df, callback_on_iter=iter_function, eval_every_x_epochs=2, stop_training_after_seconds=120)

#print(predictor.predict(when={ 'number_of_bathrooms':2, 'sqft':700, 'location':'great'}))

predictor.save('/tmp/test.lw')

#exit()
predictor = Predictor(load_from_path='/tmp/test.lw')
preds = {}
for j in range(100):
    pred = predictor.predict(when={  'sqft':1600})['number_of_rooms']['predictions'][0]
    print(pred)
    if pred not in preds:
        preds[pred] = 0
    else:
        preds[pred] += 1


print(preds)


# {'3': 31, '2': 18, '1': 23, '0': 22, '<UNCOMMON>': 1}

# {'0': 35, '<UNCOMMON>': 6, '1': 14, '3': 29, '2': 11}

# {'0': 30, '3': 32, '1': 20, '2': 13, '<UNCOMMON>': 0}

# {'2': 12, '1': 17, '3': 27, '0': 38, '<UNCOMMON>': 1}


