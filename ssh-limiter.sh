#!/bin/bash

case "$SSH_ORIGINAL_COMMAND" in
    *\&*)
        echo "UNAUTHORIZED COMMAND"
        ;;
    *\;*)
        echo "UNAUTHORIZED COMMAND"
        ;;
    *\|*)
        echo "UNAUTHORIZED COMMAND"
        ;;
    "sudo tac /var/log/syslog")
        $SSH_ORIGINAL_COMMAND
        ;;
    *)
        echo "UNAUTHORIZED COMMAND"
        ;;
esac
