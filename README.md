# My K8s Homelab

This is my Kubernetes Homelab, managed with [Kluctl](https://kluctl.io), of which I'm
also the main developer and maintainer.

It's still a very young Homelab and thus doesn't do a lot. It basically just sets up what is
usually needed (e.g. Cilium, cert-manager, ingress-nginx, metallb, ...) and then deploys a
small set of applications I need at home. This will surely grow over tine.

## Why Kluctl?

Most K8s Homelabs rely on Flux or ArgoCD to implement a GitOps style workflow. I started to
work on [Kluctl](https://kluctl.io) a few years ago as I did not feel that the existing
solutions were suitable for my needs and workflows at work. I was not aware of Flux and ArgoCD
and thus did not follow the development of the two major GitOps solutions, which resulted in
Kluctl solving the same problems with a completely different approach and point of view.

I believe that the way Kluctl solves complex deployments and configuration management fits very
well for many other people. This Homelab can hopefully show a very practical example of how
Kluctl solves things and thus motivate people to give it a try.

Next, I'll try to give a short list of main differences between Flux and Kluctl based
Homelabs.

### GitOps

Kluctl allows to implement GitOps style workflows while still allowing to revert to non-GitOps
workflows whenever needed. This is possible because Kluctl deployment projects do not rely
on CRDs and thus also don't need a controller to perform a deployment.

This in turn allows to perform deployments from your local machine, which is handy when you need
to move fast (no more push+pray iterations) and test out changes. You can also perform dry-run deploys/diffs
locally, which works even better in combination with GitOps. When you're done with your changes
and feel confident enough with the state of the deployment, committing and pushing will then allow
GitOps to take over. GitOps can either be solved via the [kluctl-controller](https://github.com/kluctl/flux-kluctl-controller)
(recommended) or via CI/CD pipelines.

### Bootstrapping

There is no need to use another tool (e.g. Ansible) to bootstrap a cluster with a CNI solution or any
other base component. Kluctl can easily install Cilium (or any other CNI) in the same deployment as any
other component that is needed for any upcoming deployments. You can really start using Kluctl on a
completely naked cluster.

### Dependencies and deployment order

Kluctl is not based on CRDs and instead relies on a hierarchical project structure. This allows for very
simple and easy dependency/order management in a declarative and predictable way.

Check [base/deployment.yaml](./kluctl/base/deployment.yaml) for example. Each deployment item is processed
in parallel until a barrier forces Kluctl to wait for completion of previous deployments. It then continues
with the next deployment items until the next barrier appears. This way, it's easy to deploy namespaces
before anything else, CRDs before CRs, and so on...

### Templating

Kluctl uses templating and [variable sources](https://kluctl.io/docs/kluctl/reference/templating/variable-sources/)
to glue together individual deployment items. Templating can be used absolutely everywhere, meaning that
everything that configuration can be used everywhere to control the deployment.

I still recommend to use templating at a minimal level, so that it doesn't get too complex. In this Homelab
deployment for example, I mostly use templating to distribute network related configuration.

## TODOs

I still plan to add a few things here and there. The most important TODOs:

1. Actually enable GitOps in this repo. This means I need to deploy the [kluctl-controller](https://github.com/kluctl/flux-kluctl-controller)
and then take over deployments of this repo.
2. Introduce Renovate to update helm-chart.yaml files. I have a working configuration already, it just needs
to be incorporated here.
3. Move away from Ansible (I hate Ansible...) and find a way to use Talos, PXE boot, and NFS for the rootfs
4. More applications :)

## Thanks

The Ansible/K3s deployment and Taskfiles are based on https://github.com/onedr0p/flux-cluster-template, which
saved me quite some time with my Raspberry PI + K3s based Homelab.
