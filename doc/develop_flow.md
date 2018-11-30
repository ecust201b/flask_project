## github 代码开发流程

1. 从公共库将代码仓库 fork 到自己的 github 账号下

2. 本机 git clone 自己账号下的仓库

    ```shell
    git clone <url>
    ```

3. 将远程公共库作为本地仓库的 remote 源, 并获取公共库的所有分支

    ```shell
    git remote add <upstream> <url>
    git remote update
    ```

    < upstream > 为公共库在本地的别名

    < url > 为公共库的 url

4. 确保此时处在 develop 或 master 分支上, 并从该分支创建新的开发分支, 该分支最好以 issue 号命名。

    ```shell
    git checkout <upstream>/<develop>
    git checkout -b <branch_name>
    ```

5. 在开发之前确保当前分支和公共库代码代码保持一致

    ```shell
    git fetch <upstream>
    git rebase <upstream>/<develop>
    ```

6. 开发完成后, commit 到本地库

    ```shell
    git add .
    git commit -am "<message>"
    ```

7. 与线上公共库代码同步, 避免出现冲突无法 merge

    ```shell
    git fetch <upstream>
    git rebase <upstream>/<develop>
    ```

    如果出现冲突, 在本地解决完冲突后再进行下一步

8. 从本地代码仓库 push 到自己的远程仓库即 origin 库

    ```shell
    git push origin <branch_name>:<branch_name>
    ```

9. 从自己的 github 发起 pr

**补充:**

合并多个 commit 的方式:

```shell
git log # 找到第一个不是自己做的 commit_id
git reset <commit_id> # reset 到那个 commit, 注意不要加 --hard, 误操作的话可以用 git reflog 再 reset 回去
git add .
git commit -am "<message>"
```

此时可能 origin 库的中当前分支 commit 超越本地仓库, push 时需要加上 --force 参数

```shell
git push --force origin <branch_name>:<branch_name>
```