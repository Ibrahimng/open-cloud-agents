# Triton Model Repository Layout & Configuration Spec

## Directory Layout
Triton Inference Server mandates a strict directory hierarchy:
```text
model_repository/
└── text_classifier/
    ├── config.pbtxt            # Model configuration, inputs, outputs, dynamic batching
    └── 1/                      # Version directory (integer)
        └── model.onnx          # Serialized ONNX binary
```

## Production `config.pbtxt` Spec
```protobuf
name: "text_classifier"
platform: "onnxruntime_onnx"
max_batch_size: 64

input [
  {
    name: "input_ids"
    data_type: TYPE_INT64
    dims: [ -1 ]
  }
]

output [
  {
    name: "probabilities"
    data_type: TYPE_FP32
    dims: [ 2 ]
  }
]

# Enable Dynamic Batching to saturate GPU tensor cores
dynamic_batching {
  max_queue_delay_microseconds: 5000
}

# GPU Instance Grouping
instance_group [
  {
    count: 2
    kind: KIND_GPU
  }
]
```

