const Redis = require('ioredis')
const pub = new Redis(6379, 'localhost')
const k8s = require('@kubernetes/client-node')

const kc = new k8s.KubeConfig();

// Path to your cluster config file
kc.loadFromFile('config');

let watch = new k8s.Watch(kc);
const nodeName = process.env.NODE || 'kube-worker4'

function publish(type, phase, podname) {
    let status = {
        type: type,
        phase: phase,
        pod: podname
    }
    pub.publish("status", JSON.stringify(status))
}

function handleStatus(type, phase, podname) {
    if (type == 'ADDED' && phase == 'Pending') {
        console.log('Pending from ADDED: ' + podname)
        publish(type, phase, podname)
   }
    else if (type == 'ADDED' && phase == 'Running') {
        console.log('Running from ADDED: ' + podname)
        publish(type, phase, podname)
    }
    else if (type == 'MODIFIED' && phase == 'Running') {
        console.log('Running from MODIFIED:', podname)
        publish(type, phase, podname)
    }
    else if (type == 'DELETED' && (phase == 'Pending' || phase == 'Running')) {
        console.log('Terminated: ' + podname + " Phase: " + phase)
        publish(type, phase, podname)
    }
}

let req = watch.watch(`/api/v1/namespaces/default/pods?fieldSelector=spec.nodeName%3D${nodeName}`,
    // optional query parameters can go here.
    {},
    // callback is called for each received object.
    (type, obj) => {
        handleStatus(type, obj.status.phase, obj.metadata.name)
    },
    // done callback is called if the watch terminates normally
    (err) => {
        if (err) {
            console.log(err);
        }
    });