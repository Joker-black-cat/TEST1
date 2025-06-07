#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "用法: $0 <文件名> <搜索内容>"
    exit 1
fi

file=$1
search_term=$2
output_file="search_results_$(date +%Y%m%d_%H%M%S).txt"

if [ ! -f "$file" ]; then
    echo "错误: 文件 $file 不存在"
    exit 1
fi

echo "在文件 $file 中搜索 '$search_term'..." | tee -a "$output_file"
echo "----------------------------------------" | tee -a "$output_file"

grep -n "$search_term" "$file" | tee -a "$output_file"

if [ $? -eq 0 ]; then
    echo "----------------------------------------" | tee -a "$output_file"
    echo "搜索结果已保存到 $output_file"
else
    echo "未找到匹配内容"
    rm "$output_file"
fi
