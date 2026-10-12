# Runtime protection and failure handling

[Home](../README.en.md) · [中文](zh/43-safety.md)

## Separate the responsibilities

The policy proposes actions. A robot adapter interprets units and frames. The controller and protective system enforce the operating envelope. Learned progress or failure monitors can provide extra signals, but do not establish a certified safety function.

| Layer | Concrete checks |
| --- | --- |
| Hardware and workspace | Validated stop functions, access control, fixtures and task hazards |
| Command interface | Joint order, units, frame, finite values and supported command mode |
| Motion limits | Hardware-appropriate position, velocity, acceleration and contact limits |
| Timing | Heartbeat, input age, inference deadline and queue starvation |
| Spatial checks | Reachable workspace, self-collision and fixture collision |
| Handover and recovery | Explicit control ownership, validated recovery conditions and human takeover |

Limits come from the robot, controller and task assessment, not from percentiles of demonstration data. Independent execution of a monitor reduces shared software failure modes, but a second ordinary process is not itself a safety-rated controller.

## Specify the failure response

For each event, record detection, response, verification and restart conditions.

| Event | Define before deployment |
| --- | --- |
| Policy crash or GPU stall | Which independent component detects it and requests the validated stop |
| Stale observation | Maximum allowed age and the response when it is exceeded |
| Buffer starvation | Controller-specific behavior while no valid command is available |
| Limit violation | Whether the command is rejected, limited or triggers a stop; log each occurrence |
| Human takeover | Which commands lose authority and how ownership is transferred |
| Restart | Preconditions, state checks and prevention of unexpected motion |

There is no universal “safe command.” Holding a pose, removing torque, retreating or releasing an object can have different consequences. Choose and validate a response for the robot and load. Fault injection starts in mocks or simulation and proceeds to controlled hardware testing under the robot's procedures.

## Logging and deployment records

Store observation timestamps, action commands, guard events, controller state and operator interventions. Bind the checkpoint to code revision, robot model, calibration, camera pose, action convention and normalization statistics using the [deployment manifest](../templates/deployment-manifest.yaml).

Changing calibration or an adapter changes the deployed system even when the model file stays the same. A rollout log should identify all of these artifacts.

## Reading standards and monitoring research

[DGUV/IFA's collaborative-robot material](https://www.dguv.de/ifa/fachinfos/kollaborierende-roboter/index-2.jsp) introduces protective measures and application-specific assessment. Applicable requirements depend on the robot system, application and jurisdiction.

[ISO 21448](https://www.iso.org/standard/77490.html) concerns road vehicles and intended-functionality hazards. It can provide conceptual background; it is not a general robot certification rule.

For research monitors, record detection latency, missed failures, false stops, calibration data and evaluation conditions. See [monitoring references](resources.md#safety) and [OGAM](resources.md#ogam-runtime-monitor).

**Completion check:** for a lost heartbeat or empty queue, identify the detecting component, validated response and restart conditions. Use [the deployment checklist](../checklists/before-deploying.md).
