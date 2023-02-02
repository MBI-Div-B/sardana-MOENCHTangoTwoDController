# sardana-MOENCHTangoTwoDController

## Description

This sardana device is the highest API to control a MOENCH detector. This device must be used in experiments.

## Getting Started

### Dependencies

* `pytango 9`
* [moenchControl TangoDS](https://github.com/lrlunin/pytango-moenchDetector)
* [moenchZmqServer TangoDS](https://github.com/lrlunin/pytango-moenchZmqServer)

## Getting Started
The sardana device has 6 axes. Different image processing algorithm corresponds to each axis:

| axis | image |
| -| ----|
| 0 | analog*   |
| 1 | analog** |
| 2 | threshold*|
| 3 | threshold** |
| 4 | counting* |
| 5 | counting**|

>*pumped if split is enabled, otherwise all frames

>**unpumped if split is enabled, otherwise empty

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* Martin Borchert
* Daniel Schick
* rest of MBI crew 
