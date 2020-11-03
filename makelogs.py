from datetime import datetime
import time


# With async messages come in before the old ones are finished meaning -
    # Cannot simply chronologically writes messages and runtime for each receive and send
        # You will get a bunch of messages received then a bunch of runtimes
    # Using a second log file that logs the UTC timestamp with the runtime
    # Count received messages in "log" and compare that count to the number of finished jobs that are logged in time_log
    # Completed.txt has an up to date list of completed jobs

def initLogs(logNames = []):
    for fname in logNames:
        with open(fname, 'w+') as f: # Make sure logs are there and empty on startup.
            pass

def createLogs(start, log):
    runTime = round(time.time() - start, 2)
    logTime = f'\t{runTime} seconds'

    with open('time_log', 'a+') as f:
        f.write(f'{start}={logTime.strip()}\n')

    with open('log', 'a+') as f:
        for line in log:
            f.write(line + '\n')
        f.write('END' + '\n') # Will use END as a placeholder.


def logCatchUp(programStart): # If requests come in before the current one is finished, the runtime is logged after the message
    timeData = open('time_log', 'r').read().splitlines()
    currentLog = [i for i in open('log', 'r').read().splitlines() if i != '\n']
    commandCt = [i.split()[0] for i in currentLog if i.startswith('Command')].count('Command') # Counts how many valid messages it received in a session
    if len(timeData) != commandCt:
        print('Catching up')
        return
    elif len(timeData) == commandCt and commandCt != 0:
        print('Writing to completed.txt')
        messageCt = 0
        revisedLog = []
        for i in currentLog:
            if i != 'END':
                if i.startswith('Command'):
                    revisedLog.append(f'({messageCt}) {i}\n')
                else:
                    revisedLog.append(f'{i}\n')
            else:
                utcAndRunTime = timeData[messageCt].split('=')
                timestamp = utcAndRunTime[0]

                intTimeStamp = int(round(eval(timestamp)))
                date = datetime.fromtimestamp(intTimeStamp).strftime('%Y-%m-%d %H:%M:%S')

                revisedLog.append(f'\tdate:\t{date}\n' )
                revisedLog.append(f'\tUTC:\t{timestamp}\n' )
                revisedLog.append(f'{utcAndRunTime[1]}\n' )
                revisedLog.append(str('─' * 125) + '\n')

                messageCt += 1


        revisedLog[-1] = revisedLog[-1].rstrip('\n')

        with open('completed.txt', 'w+') as f: #
            for i in revisedLog:
                f.write(i)

            f.write(f'\n\nmessages: {commandCt}')
            uptime = round(time.time() - programStart)
            f.write(f'\nuptime: {uptime} seconds')
