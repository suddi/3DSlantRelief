#version 330 compatibility

// -----------------------------------------------------------------
// INPUT VARIABLES
// ----------------------------------------------------------------

layout (location = 0) in vec2 vertVertex;
layout (location = 1) in vec2 vertTexCoord;
layout (location = 2) in vec3 vertNormal;

uniform mat4 ModelViewMatrix;
uniform mat4 ProjectionMatrix;
uniform mat3 NormalMatrix;

// uniform sampler2D colormap;
uniform sampler2D heightmap;
uniform sampler2D normalmap;

uniform bool process_stimuli;
uniform bool per_pixel;

// Displacement Mapping variables
const float SCALE_FACTOR = 15.0;

// Lighting variables
// const int NUM_LIGHTS = 1;
// const vec3 CAMERA_POS = vec3(0.0, 0.0, 0.0);
// const vec3 AMBIENT = vec3(0.3, 0.3, 0.3);

// uniform vec3 light_position[NUM_LIGHTS];
// uniform vec3 light_color[NUM_LIGHTS];
uniform vec3 light_direction;

// -----------------------------------------------------------------
// OUTPUT VARIABLES
// -----------------------------------------------------------------

// out vec4 fragVertex;
out vec2 fragTexCoord;
out vec3 fragNormal;
out vec3 fragColor;

// out vec3 camera_vector;
// out vec3 light_vector[NUM_LIGHTS];

// -----------------------------------------------------------------
// RGB TO GREYSCALE FUNCTIONS
// -----------------------------------------------------------------

/*
float convert_average(vec4 pixel) {
    return (pixel.r + pixel.g + pixel.b) / 3.0;
}
*/

/*
float convert_luminance(vec4 pixel) {
    return (0.30 * pixel.r) + (0.59 * pixel.g) + (0.11 * pixel.b);
}
*/

float convert_luminance(vec4 pixel) {
    return (0.2126 * pixel.r) + (0.7152 + pixel.g) + (0.0722 * pixel.b);
}

/*
float convert_desaturation(vec4 pixel) {
    float mx;
    float mn;

    mx = max(pixel.r, pixel.g);
    mx = max(mx, pixel.b);

    mn = min(pixel.r, pixel.g);
    mn = min(mn, pixel.b);
    return (mx + mn) / 2.0;
}
*/

// -----------------------------------------------------------------
// HANDLE NORMALS
// -----------------------------------------------------------------

vec3 get_normal(void) {
    // Get pixel values for TexCoord
    vec4 pixel = texture(normalmap, vertTexCoord.st);
    return vec3(pixel.r, pixel.g, pixel.b);
}

// -----------------------------------------------------------------
// HANDLE DISPLACEMENT MAPPING
// -----------------------------------------------------------------

vec4 displacement_mapping(void) {
    vec4 pixel = texture(heightmap, vertTexCoord.st);

    // Convert RGB to grey value
    float grey_value = convert_luminance(pixel);

    // Return displaced position coordinates
    return vec4(vertNormal * grey_value * SCALE_FACTOR, 0.0) + vec4(vertVertex, 0.0, 1.0);
}

// -----------------------------------------------------------------
// HANDLE LIGHTING
// -----------------------------------------------------------------

/*
void vertex2camera(vec4 vertex) {
    // Set the vector from the vertex to the camera
    camera_vector = CAMERA_POS - vertex.xyz;
}
*/

/*
void vertex2light(vec4 vertex) {
    // Set the vectors from the vertex to each light
    for(int i = 0; i < NUM_LIGHTS; ++i)
        light_vector[i] = light_position[i] - vertex.xyz;
}
*/

void directional_lighting(vec3 normal) {
    vec3 diffuse = vec3(1.0, 1.0, 1.0);

    float intensity = max(dot(normal, light_direction), 0.0);
    // // intensity = (intensity - 0.3) * 10.0;
    // if (intensity >= 0.45)
    //     fragColor = 1.0 * vec3(1.0, 0.0, 0.0);
    // else if (intensity >= 0.4)
    //     fragColor = 1.0 * vec3(0.0, 1.0, 0.0);
    // else if (intensity < 0.3)
    //     fragColor = 1.0 * vec3(0.0, 0.0, 1.0);
    // fragColor = normal;
    // fragColor = normal * 100.0;

    fragColor = intensity * diffuse;
}

// -----------------------------------------------------------------
// MAIN FUNCTION
// -----------------------------------------------------------------

void main(void) {
    fragTexCoord = vertTexCoord.st;
    vec4 fragVertex = displacement_mapping();
    fragNormal = transpose(inverse(NormalMatrix)) * get_normal();

    if (!per_pixel && process_stimuli)
        directional_lighting(fragNormal);
    gl_Position = ProjectionMatrix * (ModelViewMatrix * fragVertex);
}
