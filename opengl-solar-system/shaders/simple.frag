#version 330 core

in vec3 fragPos;
in vec3 fragNormal;
in vec2 fragTexCoord;
in vec2 fragCloudCoord;

uniform sampler2D textureSampler;
uniform sampler2D cloudSampler;
uniform vec3 lightPos;
uniform vec3 light2Pos;
uniform vec3 viewPos;
uniform vec3 lightColor;
uniform vec3 light2Color;
uniform bool isLightSource;
uniform bool isEarth;

out vec4 outColor;

vec3 calcLight(vec3 lightP, vec3 lightC, vec3 norm, vec3 viewDir, vec3 fragP)
{
    float ambientStrength = 0.15;
    vec3 ambient = ambientStrength * lightC;

    vec3 lightDir = normalize(lightP - fragP);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightC * 1.2;

    float specularStrength = 0.9;
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * lightC;

    return ambient + diffuse + specular;
}

void main()
{
    vec3 objectColor = texture(textureSampler, fragTexCoord).rgb;

    if (isEarth) {
    vec3 cloudColor = texture(cloudSampler, fragCloudCoord).rgb;
    float cloudMask = dot(cloudColor, vec3(0.299, 0.587, 0.114));
    cloudMask = smoothstep(0.4, 0.7, cloudMask);
    cloudMask = clamp(cloudMask * 1.2, 0.0, 1.0);
    objectColor = mix(objectColor, vec3(1.0), cloudMask * 0.35);
}

    if (isLightSource) {
        outColor = vec4(objectColor, 1.0);
        return;
    }

    vec3 norm = normalize(fragNormal);
    vec3 viewDir = normalize(viewPos - fragPos);

    vec3 light1 = calcLight(lightPos, lightColor, norm, viewDir, fragPos);
    vec3 light2 = calcLight(light2Pos, light2Color, norm, viewDir, fragPos);

    vec3 result = clamp((light1 + light2) * objectColor, 0.0, 1.0);
    outColor = vec4(result, 1.0);
}