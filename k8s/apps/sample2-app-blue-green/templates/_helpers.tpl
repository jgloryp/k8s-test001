{{/*
sample2-app Blue-Green Helm 템플릿 헬퍼 함수들
*/}}

{{/*
Expand the name of the chart.
*/}}
{{- define "sample2-app-blue-green.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "sample2-app-blue-green.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sample2-app-blue-green.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sample2-app-blue-green.labels" -}}
helm.sh/chart: {{ include "sample2-app-blue-green.chart" . }}
{{ include "sample2-app-blue-green.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
environment: {{ .Values.environment | default "default" }}
deployment-strategy: blue-green
{{- end }}

{{/*
Selector labels for the main service
*/}}
{{- define "sample2-app-blue-green.selectorLabels" -}}
app.kubernetes.io/name: sample2-app
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Blue version labels
*/}}
{{- define "sample2-app-blue-green.blueLabels" -}}
{{ include "sample2-app-blue-green.selectorLabels" . }}
version: blue
{{- end }}

{{/*
Green version labels
*/}}
{{- define "sample2-app-blue-green.greenLabels" -}}
{{ include "sample2-app-blue-green.selectorLabels" . }}
version: green
{{- end }}

{{/*
Active version selector labels
*/}}
{{- define "sample2-app-blue-green.activeVersionLabels" -}}
{{ include "sample2-app-blue-green.selectorLabels" . }}
version: {{ .Values.activeVersion }}
{{- end }}