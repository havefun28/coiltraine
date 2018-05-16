import os
import re

from logger import json_formatter
from configs import g_conf
from utils.general import sort_nicely
# Check the log and also put it to tensorboard



def get_current_iteration(exp):
    """

    Args:
        exp:

    Returns:
        The number of iterations this experiments has already run in this mode.
        ( Depends on validation etc...

    """
    # TODO:

    pass


def get_latest_output(data):

    # Find the one that has an iteration .........
    if 'Iteration' in data[-1]:
        return data[-1]
    else:
        return data[-2]


def get_summary(data):


    # IT HAS TO BE ITERATING  ! ! !  ! ! !
    for i in range(1, len(data)):
        # Find the
        if 'Summary' in data[-i]['Iterating']:
            return data[-i]
    else:  # NO SUMMARY YET COMPUTED
        return ''


def get_latest_checkpoint():


    # The path for log

    csv_file_path = os.path.join('_logs', g_conf.EXPERIMENT_BATCH_NAME,
                                 g_conf.EXPERIMENT_NAME, g_conf.PROCESS_NAME + '_csv')

    csv_files = os.listdir(csv_file_path)

    if csv_files == []:
        return None

    sort_nicely(csv_files)

    #data = json_formatter.readJSONlog(open(log_file_path, 'r'))

    return int(re.findall('\d+', csv_files[-1])[0])


def get_status(exp_batch, experiment, process_name):

    """

    Args:
        exp_batch: The experiment batch name
        experiment: The experiment name.

    Returns:
        A status that is a vector with two fields
        [ Status, Summary]

        Status is from the set = (Does Not Exist, Not Started, Loading, Iterating, Error, Finished)
        Summary constains a string message summarizing what is happening on this phase.

        * Not existent
        * To Run
        * Running
            * Loading - sumarize position ( Briefly)
            * Iterating  - summarize
        * Error ( Show the error)
        * Finished ( Summarize)

    """


    # Configuration file path
    config_file_path = os.path.join('configs', exp_batch, experiment + '.yaml')

    # The path for log
    log_file_path = os.path.join('_logs', exp_batch, experiment, process_name)

    # First we check if the experiment exist

    if not os.path.exists(config_file_path):

        return ['Does Not Exist', '']


    # The experiment exist ! However, check if the log file exist.

    if not os.path.exists(log_file_path):

        return ['Not Started', '']

    # Read the full json file.
    data = json_formatter.readJSONlog(open(log_file_path, 'r'))


    # Now check if the latest data is loading
    if 'Loading' in data[-1]:
        return ['Loading', '']

    # Then we check if finished or is going on

    if 'Iterating' in data[-1]:
        try:
            iteration_number = list(data[-1].values())[0]['Checkpoint']
        except KeyError:
            iteration_number = list(data[-1].values())[0]['Iteration']

        if iteration_number >= g_conf.NUMBER_ITERATIONS:
            return ['Finished', ' ']
        else:
            if 'validation' in process_name:
                return ['Iterating', [get_latest_output(data), get_summary(data)]]
            elif 'train' in process_name:
                return ['Iterating', get_latest_output(data)]

    # TODO: there is the posibility of some race conditions on not having error as last
    if 'Error' in data[-1]:
        return ['Error', ' ']


    raise ValueError(" No valid status found")




"""
COLOR CODINGS
"""
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
ITALIC = '\033[3m'
RED = '\033[91m'
LIGHT_GREEN = '\033[32m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
DARK_BLUE = '\033[94m'
BLUE = '\033[94m'
END = '\033[0m'


def print_train_summary(summary):

    if summary == '':
        return
    print ('        SUMMARY:')
    print ('            Iteration: ', BLUE + str(summary['Iteration']) + END)
    print ('            Images/s: ', BOLD + str(summary['Images/s']) + END)
    print ('            Loss: ', UNDERLINE + str(summary['Loss']) + END)
    print ('            Best Loss: ', LIGHT_GREEN + UNDERLINE + str(summary['BestLoss']) + END)
    print ('            Best Loss Iteration: ', BLUE + UNDERLINE + str(summary['BestLossIteration']) + END)
    #print ('            Best Error: ',UNDERLINE + str(summary['BestError']) + END)
    print ('            Outputs: ', UNDERLINE + str(summary['Output']) + END)
    print ('            Ground Truth: ', UNDERLINE + str(summary['GroundTruth']) + END)
    print ('            Error: ', UNDERLINE + str(summary['Error']) + END)



def print_validation_summary(current, latest, verbose):

    if current == '':
        return




    print ('        CHECKPOINT: ', DARK_BLUE + str(current['Checkpoint']) + END)
    if  verbose:
        print ('        CURRENT: ')
        print ('            Iteration: ', BLUE + str(current['Iteration']) + END)
        print ('            Mean Error: ', UNDERLINE + str(current['MeanError']) + END)
        print ('            Loss: ', UNDERLINE + str(current['Loss']) + END)
        print ('            Outputs: ', UNDERLINE + str(current['Output']) + END)
        print ('            Ground Truth: ', UNDERLINE + str(current['GroundTruth']) + END)
        print ('            Error: ', UNDERLINE + str(current['Error']) + END)

    if latest == '':
        return

    print ('        LATEST: ')
    print ('            Loss: ', UNDERLINE + str(latest['Loss']) + END)
    print ('            Best Loss: ', LIGHT_GREEN + UNDERLINE + str(latest['BestLoss']) + END)
    print ('            Best Loss Checkpoint: ', BLUE + UNDERLINE + str(latest['BestLossCheckpoint']) + END)
    print ('            Error: ', UNDERLINE + str(latest['Error']) + END)
    print ('            Best Error: ', LIGHT_GREEN + UNDERLINE + str(latest['BestError']) + END)
    print ('            Best Error Checkpoint: ', BLUE + UNDERLINE + str(latest['BestErrorCheckpoint']) + END)


def print_drive_summary(summary, current, verbose):


    print ('        CHECKPOINT: ', DARK_BLUE + str(current['Checkpoint']) + END)
    if verbose:
        print ('        CURRENT: ')
        print ('            Episode: ', BLUE + str(current['Iteration']) + END)
        print ('            Completed: ', GREEN + UNDERLINE + str(current['MeanError']) + END)

    print ('        LATEST: ')

    print ('            Episode: ', BLUE + str(current['Iteration']) + END)
    print ('            Completed: ', GREEN + UNDERLINE + str(current['MeanError']) + END)
    print ('            Episode: ', BLUE + str(current['Iteration']) + END)
    print ('            Completed: ', GREEN + UNDERLINE + str(current['MeanError']) + END)


def plot_folder_summaries(exp_batch, train, validation_datasets, drive_environments, verbose=False):

    # TODO: if train is not running the user should be warned

    os.system('clear')
    process_names = []
    if train:
        process_names.append('train')

    for val in validation_datasets:
        process_names.append('validation' + '_' + val)


    for drive in drive_environments:
        process_names.append('drive' + '_' + drive)


    experiments_list = os.listdir(os.path.join('configs', exp_batch))

    experiments_list = [experiment.split('.')[-2] for experiment in experiments_list]

    for experiment in experiments_list:


        # TODO: DO THE EXPERIMENT NAMER
        print (BOLD + experiment + END)

        for process in process_names:
            output = get_status(exp_batch, experiment, process)
            status  = output[0]
            summary = output[1]
            print ('    ', process)

            if status == 'Not Started':

                print ('       STATUS: ', BOLD + status + END)

            elif status == 'Iterating' or status == 'Loading':

                print('        STATUS: ', YELLOW + status + END)

            elif status == 'Finished':

                print('        STATUS: ', GREEN + status + END)

            elif status == 'Error':

                print('        STATUS: ', RED + status + END)


            if status == 'Iterating':
                if 'train' in process:
                    print_train_summary(summary[status])
                if 'validation' in process:
                    print_validation_summary(summary[0][status], summary[1][status]['Summary'], verbose)
                if 'drive' in process:
                    print_drive_summary(summary[status])





    # For each on the folder
    # Get the status.


