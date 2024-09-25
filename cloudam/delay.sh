#!/bin/bash

docker pull gaiaadm/pumba:latest || true

docker run -it --rm --name pumba01 --network host --pid host -v /var/run/docker.sock:/var/run/docker.sock gaiaadm/pumba netem --duration 10m loss --percent 90 node01
