#!/bin/sh

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/mongod
DESC=database

NAME=mongod
CONF=/etc/mongod.conf
PIDFILE=/var/run/$NAME.pid

# Handle NUMA access to CPUs (SERVER-3574)
NUMACTL_ARGS="--interleave=all"
if which numactl >/dev/null 2>/dev/null && numactl $NUMACTL_ARGS ls / >/dev/null 2>/dev/null
then
    NUMACTL="`which numactl` -- $NUMACTL_ARGS"
    DAEMON_OPTS=${DAEMON_OPTS:-"--config $CONF"}
else
    NUMACTL=""
    DAEMON_OPTS="-- "${DAEMON_OPTS:-"--config $CONF"}
fi

. /lib/lsb/init-functions

STARTTIME=1
DIETIME=10

DAEMONUSER=${DAEMONUSER:-mongodb}
DAEMONGROUP=${DAEMONGROUP:-mongodb}

set -e

running_pid() {
    pid=$1
    name=$2
    [ -z "$pid" ] && return 1
    [ ! -d /proc/$pid ] &&  return 1
    cmd=`cat /proc/$pid/cmdline | tr "\000" "\n"|head -n 1 |cut -d : -f 1`
    # Is this the expected server
    [ "$cmd" != "$name" ] &&  return 1
    return 0
}

running() {
# Check if the process is running looking at /proc
# (works for all users)

    # No pidfile, probably no daemon present
    [ ! -f "$PIDFILE" ] && return 1
    pid=`cat $PIDFILE`
    running_pid $pid $DAEMON || return 1
    return 0
}

start_server() {
            # Recommended ulimit values for mongod or mongos
            # See http://docs.mongodb.org/manual/reference/ulimit/#recommended-settings
            #
            ulimit -f unlimited
            ulimit -t unlimited
            ulimit -v unlimited
            ulimit -n 64000
            ulimit -m unlimited

            # In dash, ulimit takes -p for maximum user processes
            # In bash, it's -u
            if readlink /proc/$$/exe | grep -q dash
            then
                    ulimit -p 64000
            else
                    ulimit -u 64000
            fi

            # Start the process using the wrapper
            start-stop-daemon --background --start --quiet --pidfile $PIDFILE \
                        --make-pidfile --chuid $DAEMONUSER:$DAEMONGROUP \
                        --exec $NUMACTL $DAEMON $DAEMON_OPTS
            errcode=$?
        return $errcode
}

stop_server() {
# Stop the process using the wrapper
            start-stop-daemon --stop --quiet --pidfile $PIDFILE \
                        --retry 300 \
                        --user $DAEMONUSER \
                        --exec $DAEMON
            errcode=$?
        return $errcode
}

force_stop() {
# Force the process to die killing it manually
        [ ! -e "$PIDFILE" ] && return
        if running ; then
                kill -15 $pid
                sleep "$DIETIME"s
                if running ; then
                        kill -9 $pid
                        sleep "$DIETIME"s
                        if running ; then
                                echo "Cannot kill $NAME (pid=$pid)!"
                                exit 1
                        fi
                fi
        fi
        rm -f $PIDFILE
}


case "$1" in
  start)
        log_daemon_msg "Starting $DESC" "$NAME"
        # Check if it's running first
        if running ;  then
            log_progress_msg "apparently already running"
            log_end_msg 0
            exit 0
        fi
        if start_server ; then
            # NOTE: Some servers might die some time after they start,
            # this code will detect this issue if STARTTIME is set
            # to a reasonable value
            [ -n "$STARTTIME" ] && sleep $STARTTIME # Wait some time
            if  running ;  then
                # It's ok, the server started and is running
                log_end_msg 0
            else
                # It is not running after we did start
                log_end_msg 1
            fi
        else
            # Either we could not start it
            log_end_msg 1
        fi
        ;;
  stop)
        log_daemon_msg "Stopping $DESC" "$NAME"
        if running ; then
            # Only stop the server if we see it running
                        errcode=0
            stop_server || errcode=$?
            log_end_msg $errcode
        else
            # If it's not running don't do anything
            log_progress_msg "apparently not running"
            log_end_msg 0
            exit 0
        fi
        ;;
  force-stop)
        # First try to stop gracefully the program
        $0 stop
        if running; then
            # If it's still running try to kill it more forcefully
            log_daemon_msg "Stopping (force) $DESC" "$NAME"
                        errcode=0
            force_stop || errcode=$?
            log_end_msg $errcode
        fi
        ;;
  restart)
        log_daemon_msg "Restarting $DESC" "$NAME"
                errcode=0
        stop_server || errcode=$?
        # Wait some sensible amount, some server need this
        [ -n "$DIETIME" ] && sleep $DIETIME
        start_server || errcode=$?
        [ -n "$STARTTIME" ] && sleep $STARTTIME
        running || errcode=$?
        log_end_msg $errcode
        ;;
  status)

        log_daemon_msg "Checking status of $DESC" "$NAME"
        if running ;  then
            log_progress_msg "running"
            log_end_msg 0
        else
            log_progress_msg "apparently not running"
            log_end_msg 1
            exit 1
        fi
        ;;
esac

exit 0